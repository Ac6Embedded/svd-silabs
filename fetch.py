#!/usr/bin/env python3
"""Fetch Silicon Labs CMSIS SVD files from the official Silicon Labs pack repo.

Python 3 stdlib only. Re-runnable: per-pack state is kept in .work/state/ and
finished packs are skipped, so you can interrupt and restart at any time.

Incremental mode (the default when manifest.json exists): only the pack index
SiliconLabs.pidx is downloaded (a small metadata file). Each pack's latest
version is compared against the recorded version in manifest.json sources[].
If nothing changed the script prints 'up to date', downloads zero pack
artifacts, touches no tracked file, and exits 0. If some packs changed, only
those packs are downloaded and re-extracted (same die dedupe rules and
also_covers bookkeeping), only their <Family> files are replaced, and
manifest.json is rewritten with the new versions, files, stats, and the
current date in 'generated'. A source that failed to download keeps its old
files and manifest entry, and the script exits 1.

Full-fetch mode (when manifest.json is missing or unreadable):
1. Download SiliconLabs.pidx (the vendor pack index).
2. Select packs named GeckoPlatform_*_DFP plus Wiseconnect_SIWG917_DFP.
   Legacy packs at 5.8.10 (names without the GeckoPlatform_ prefix) are skipped,
   they are superseded by the GeckoPlatform packs.
3. For each pack: download the .pack (a zip), list SVD/ entries, group files by
   die key (device name up to the first F<digits> flash code), extract only the
   lexicographically last file of each group, record the rest as also_covers.
   The pack file is deleted after extraction to save disk.
4. Validate every extracted SVD with xml.etree (well-formed, root == device).
5. If the family tree exceeds the size budget, escalate the dedupe key by also
   stripping trailing OPN digits from the die key and drop the extra files.
6. Write manifest.json.

A missing family directory with a manifest present is handled by the incremental
path too: every source is then detected as 'local files missing' and re-fetched,
which yields a complete build.

Usage: python fetch.py
"""

import json
import os
import re
import shutil
import stat
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import OrderedDict
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, ".work")
STATE = os.path.join(WORK, "state")
PACKS = os.path.join(WORK, "packs")
# The SVD family folders now live directly at the repo root, so the output base
# is ROOT itself; family files are written to SVD_BASE/<Family>/<device>.svd.
SVD_BASE = ROOT
LIC_DIR = os.path.join(ROOT, "LICENSES")

# Repo entries that are never family output directories. clean_family_dirs()
# must skip these so a full rebuild can reset the SVD tree without ever touching
# the repository itself (.git and friends) when SVD_BASE == ROOT.
PROTECTED = {".git", ".github", ".gitignore", ".work", "LICENSES",
             "README.md", "manifest.json", "fetch.py"}

BASE = "https://www.silabs.com/documents/public/cmsis-packs/"
PIDX_URL = BASE + "SiliconLabs.pidx"
UA = "Mozilla/5.0"
SIZE_BUDGET = int(1.2 * 1024 ** 3)  # ~1.2 GB working tree budget

# Number of pack artifacts downloaded this run (the pidx index is not counted,
# it is a small metadata file fetched on every run).
DOWNLOADS = [0]


def log(msg):
    print(msg, flush=True)


def _on_rm_error(func, path, _exc):
    """shutil.rmtree onerror handler: clear the read-only bit and retry.

    Needed on Windows where a read-only file makes os.remove raise.
    """
    try:
        os.chmod(path, stat.S_IWRITE)
    except OSError:
        pass
    func(path)


def family_dirs():
    """Yield absolute paths of the family output directories at the repo root.

    Every child directory of ROOT that is not a protected repo entry is a
    family folder (EFR32MG24, BGM13, ...). SVD_BASE == ROOT, so this is how the
    SVD tree is enumerated now that it lives at the top level.
    """
    for name in os.listdir(ROOT):
        path = os.path.join(ROOT, name)
        if os.path.isdir(path) and name not in PROTECTED:
            yield path


def clean_family_dirs():
    """Full-rebuild cleanup: remove only family directories, never repo files.

    SVD_BASE is the repo root, so a blanket rmtree(SVD_BASE) would delete the
    whole repository including .git. This removes just the family folders and
    always skips the PROTECTED entries.
    """
    for path in family_dirs():
        shutil.rmtree(path, onerror=_on_rm_error)


def http_get(url, dest, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
                shutil.copyfileobj(r, f, 1 << 20)
            return True
        except Exception as e:  # noqa: BLE001
            last = e
            log("  retry %d for %s: %s" % (i + 1, url, e))
            time.sleep(2 * (i + 1))
    log("  FAILED %s: %s" % (url, last))
    return False


def select_packs(pidx_path):
    tree = ET.parse(pidx_path)
    out = []
    for p in tree.getroot().iter("pdsc"):
        name = p.get("name")
        ver = p.get("version")
        if (name.startswith("GeckoPlatform_") and name.endswith("_DFP")) or \
                name == "Wiseconnect_SIWG917_DFP":
            out.append((name, ver))
    out.sort()
    return out


def family_of(pack_name):
    # GeckoPlatform_EFR32MG24_DFP -> EFR32MG24, Wiseconnect_SIWG917_DFP -> SIWG917
    parts = pack_name.split("_")
    return "_".join(parts[1:-1])


DIE_RE = re.compile(r"F\d")


def die_key(stem):
    """Device name up to (excluding) the first F<digits> flash code.

    EFR32MG24B220F1536IM48 -> EFR32MG24B220. The F in EFM32/EFR32 is followed
    by a letter, so it does not match. Names without F<digits> map to themselves.
    """
    m = DIE_RE.search(stem)
    return stem[: m.start()] if m else stem


def escalated_key(key):
    # EFR32MG24B220 -> EFR32MG24B (strip trailing OPN digits)
    return re.sub(r"\d+$", "", key)


def local_tag(tag):
    return tag.rsplit("}", 1)[-1]


def validate_svd(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return "parse error: %s" % e
    if local_tag(root.tag) != "device":
        return "root element is %r, not device" % root.tag
    return None


def extract_license(zf, pack_name, version):
    """Find the pack license via the pdsc <license> element, copy it to LICENSES/."""
    pdsc_names = [n for n in zf.namelist() if n.lower().endswith(".pdsc") and "/" not in n]
    lic_entry = None
    for pn in pdsc_names:
        try:
            root = ET.fromstring(zf.read(pn))
        except ET.ParseError:
            continue
        for el in root.iter():
            if local_tag(el.tag) == "license" and el.text and el.text.strip():
                cand = el.text.strip().replace("\\", "/").lstrip("/")
                if cand in zf.namelist():
                    lic_entry = cand
                elif "./" + cand in zf.namelist():
                    lic_entry = "./" + cand
                break
    if lic_entry is None:
        for n in zf.namelist():
            if re.search(r"licen[sc]e", os.path.basename(n), re.I):
                lic_entry = n
                break
    if lic_entry is None:
        return None
    os.makedirs(LIC_DIR, exist_ok=True)
    base = os.path.basename(lic_entry)
    dest = os.path.join(LIC_DIR, "%s-%s" % (pack_name, base))
    with open(dest, "wb") as f:
        f.write(zf.read(lic_entry))
    return {"pack": pack_name, "version": version, "entry": lic_entry,
            "saved_as": os.path.relpath(dest, ROOT).replace(os.sep, "/")}


def process_pack(name, version, lic_done, force_license=False):
    """Download one pack, extract deduped SVDs, write state file. Returns state."""
    state_path = os.path.join(STATE, name + ".json")
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as f:
            st = json.load(f)
        if st.get("version") == version and not st.get("failed"):
            fam_dir = os.path.join(SVD_BASE, st.get("family", family_of(name)))
            if all(os.path.exists(os.path.join(fam_dir, g["picked"] + ".svd"))
                   for g in st.get("groups", {}).values()):
                return st
        # stale state (old version, failed, or extracted files gone): redo it

    fam = family_of(name)
    url = "%sSiliconLabs.%s.%s.pack" % (BASE, name, version)
    pack_path = os.path.join(PACKS, "%s.%s.pack" % (name, version))
    log("pack %s %s" % (name, version))
    if not os.path.exists(pack_path):
        log("  downloading artifact %s" % url)
        DOWNLOADS[0] += 1
        if not http_get(url, pack_path):
            st = {"name": name, "version": version, "url": url, "family": fam,
                  "failed": True, "groups": {}, "invalid": []}
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(st, f, indent=1)
            return st

    st = {"name": name, "version": version, "url": url, "family": fam,
          "failed": False, "groups": {}, "invalid": [], "license": None}
    with zipfile.ZipFile(pack_path) as zf:
        svd_entries = [n for n in zf.namelist()
                       if n.lower().endswith(".svd")
                       and "svd/" in n.lower().replace("\\", "/")]
        if not svd_entries:  # fall back: any .svd anywhere in the pack
            svd_entries = [n for n in zf.namelist() if n.lower().endswith(".svd")]
        groups = {}
        for entry in svd_entries:
            stem = os.path.splitext(os.path.basename(entry))[0]
            groups.setdefault(die_key(stem), []).append((stem, entry))
        fam_dir = os.path.join(SVD_BASE, fam)
        os.makedirs(fam_dir, exist_ok=True)
        # each pack owns its family dir; drop old files before re-extracting
        for fn in os.listdir(fam_dir):
            if fn.lower().endswith(".svd"):
                os.remove(os.path.join(fam_dir, fn))
        for key in sorted(groups):
            members = sorted(groups[key])  # lexicographic by stem
            pick_stem, pick_entry = members[-1]
            dest = os.path.join(fam_dir, pick_stem + ".svd")
            with zf.open(pick_entry) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out)
            err = validate_svd(dest)
            if err:
                os.remove(dest)
                st["invalid"].append({"device": pick_stem, "error": err})
                continue
            st["groups"][key] = {
                "picked": pick_stem,
                "covers": [s for s, _ in members if s != pick_stem],
            }
        need_lic = force_license or version not in lic_done
        if need_lic:
            info = extract_license(zf, name, version)
            if info:
                st["license"] = info
                lic_done[version] = info
    os.remove(pack_path)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=1)
    log("  %d svd entries, kept %d, invalid %d" %
        (len(svd_entries), len(st["groups"]), len(st["invalid"])))
    return st


def tree_size(path):
    total = 0
    for dirpath, _dirs, files in os.walk(path):
        for fn in files:
            total += os.path.getsize(os.path.join(dirpath, fn))
    return total


def svd_tree_size():
    """Total bytes of the SVD tree: the sum over the family directories only.

    SVD_BASE == ROOT, so walking SVD_BASE directly would also count .git, .work
    and the other repo files. Summing per family folder measures exactly the
    same content the old tree_size(ROOT / "svd") did.
    """
    return sum(tree_size(path) for path in family_dirs())


def escalate(states):
    """Second-level dedupe: strip trailing OPN digits from the die key.

    The lexicographically last file of an escalated group is always the pick of
    its own die group, so it is already on disk. Remove the other picks.
    """
    removed = 0
    for st in states:
        if st.get("failed") or not st["groups"]:
            continue
        fam_dir = os.path.join(SVD_BASE, st["family"])
        merged = {}
        for key, g in st["groups"].items():
            merged.setdefault(escalated_key(key), []).append(g)
        new_groups = {}
        for ekey, gs in merged.items():
            all_files = sorted(set(f for g in gs for f in [g["picked"]] + g["covers"]))
            pick = max(g["picked"] for g in gs)
            for g in gs:
                if g["picked"] != pick:
                    p = os.path.join(fam_dir, g["picked"] + ".svd")
                    if os.path.exists(p):
                        os.remove(p)
                        removed += 1
            new_groups[ekey] = {"picked": pick,
                                "covers": [f for f in all_files if f != pick]}
        st["groups"] = new_groups
    log("escalated dedupe removed %d files" % removed)
    return removed


def source_license(st):
    """Sniff the embedded license of the first extracted file of a source.

    Every pack ships a License/license.md that points at the Silicon Labs MSLA.
    On top of that, Series 0/1 SVDs embed the Zlib license in <licenseText> and
    the SIWG917 SVDs embed an ARM freely-distributable notice.
    """
    for key in sorted(st["groups"]):
        p = os.path.join(SVD_BASE, st["family"],
                         st["groups"][key]["picked"] + ".svd")
        if not os.path.exists(p):
            continue
        with open(p, "rb") as f:
            head = f.read(4096).decode("utf-8", errors="replace")
        if "SPDX-License-Identifier: Zlib" in head:
            return "MSLA (pack license); SVD files embed Zlib (SPDX)"
        if "freely distributed" in head:
            return "MSLA (pack license); SVD files embed ARM freely-distributable notice"
        return "MSLA (pack license); no license text inside SVD files"
    return "MSLA (pack license)"


def build_manifest(states, dedupe_level):
    sources = []
    files = []
    total_bytes = 0
    for st in sorted(states, key=lambda s: s["name"]):
        if st.get("failed"):
            sources.append({"name": st["name"], "url": st["url"],
                            "version": st["version"],
                            "license": "download failed", "files": []})
            continue
        src_files = []
        for key in sorted(st["groups"]):
            g = st["groups"][key]
            rel = "%s/%s.svd" % (st["family"], g["picked"])
            abs_p = os.path.join(ROOT, rel.replace("/", os.sep))
            if not os.path.exists(abs_p):
                continue
            total_bytes += os.path.getsize(abs_p)
            src_files.append(rel)
            entry = {"path": rel, "device": g["picked"], "family": st["family"],
                     "source": st["name"], "provenance": "pristine"}
            if g["covers"]:
                entry["also_covers"] = g["covers"]
            files.append(entry)
        sources.append({"name": st["name"], "url": st["url"],
                        "version": st["version"],
                        "license": st.get("license_note") or source_license(st),
                        "files": src_files})
    manifest = OrderedDict()
    manifest["vendor"] = "Silicon Labs"
    manifest["generated"] = date.today().isoformat()
    manifest["dedupe"] = {
        "level": dedupe_level,
        "rule": ("one SVD per die key (device name up to the first F<digits> "
                 "flash code); other parts of the group listed in also_covers"
                 if dedupe_level == "die"
                 else "one SVD per escalated key (die key with trailing OPN "
                      "digits stripped); other parts listed in also_covers"),
    }
    manifest["sources"] = sources
    manifest["files"] = sorted(files, key=lambda e: e["path"])
    manifest["stats"] = {"total_files": len(files), "total_bytes": total_bytes}
    with open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    return manifest


def load_manifest():
    """Return the parsed manifest.json, or None if missing or unusable."""
    path = os.path.join(ROOT, "manifest.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            m = json.load(f)
    except (OSError, ValueError) as e:
        log("cannot read manifest.json (%s), falling back to full fetch" % e)
        return None
    if not m.get("sources"):
        return None
    return m


def reconstruct_state(source, file_entries, level):
    """Rebuild a pack state from manifest data for a source that did not change.

    Group keys are re-derived from the picked device name with the same die key
    (and, at level die+opn, escalated key) rules used by the original fetch, so
    manifest output ordering is identical to what a full fetch would produce.
    """
    fam = file_entries[0]["family"] if file_entries else family_of(source["name"])
    st = {"name": source["name"], "version": source["version"],
          "url": source["url"], "family": fam, "failed": False,
          "groups": {}, "invalid": [], "license_note": source.get("license")}
    for e in file_entries:
        key = die_key(e["device"])
        if level == "die+opn":
            key = escalated_key(key)
        st["groups"][key] = {"picked": e["device"],
                             "covers": e.get("also_covers", [])}
    return st


def incremental_update(packs, manifest):
    """Refresh only the packs whose index version differs from manifest.json.

    Returns the exit code: 0 when up to date or updated, 1 if a pack failed.
    """
    level = manifest.get("dedupe", {}).get("level", "die")
    old_sources = OrderedDict((s["name"], s) for s in manifest["sources"])
    files_by_source = {}
    for e in manifest.get("files", []):
        files_by_source.setdefault(e["source"], []).append(e)

    latest = dict(packs)
    changed = []
    for name, version in packs:
        old = old_sources.get(name)
        if old is None:
            changed.append((name, version, "new pack"))
            continue
        if old.get("version") != version:
            changed.append((name, version,
                            "version %s -> %s" % (old.get("version"), version)))
            continue
        have = [os.path.join(ROOT, p.replace("/", os.sep))
                for p in old.get("files", [])]
        if not have or not all(os.path.exists(p) for p in have):
            changed.append((name, version, "local files missing"))
    removed = [n for n in old_sources if n not in latest]

    if not changed and not removed:
        log("up to date")
        log("artifact downloads: 0")
        return 0

    changed_names = set(n for n, _v, _w in changed)
    states = []
    for name in old_sources:
        if name in latest and name not in changed_names:
            states.append(reconstruct_state(old_sources[name],
                                            files_by_source.get(name, []),
                                            level))

    for name in removed:
        log("removed upstream: %s, deleting its files" % name)
        for e in files_by_source.get(name, []):
            p = os.path.join(ROOT, e["path"].replace("/", os.sep))
            if os.path.exists(p):
                os.remove(p)
        fam_dir = os.path.join(SVD_BASE, family_of(name))
        if os.path.isdir(fam_dir) and not os.listdir(fam_dir):
            os.rmdir(fam_dir)

    # versions of unchanged sources already have a representative license file
    lic_done = {}
    for st in states:
        lic_done[st["version"]] = True

    errors = []
    new_states = []
    for name, version, why in changed:
        log("update %s: %s" % (name, why))
        state_path = os.path.join(STATE, name + ".json")
        if os.path.exists(state_path):
            os.remove(state_path)
        # refresh this pack's own LICENSES/ file if it is a license representative
        force_lic = os.path.isdir(LIC_DIR) and any(
            fn.startswith(name + "-") for fn in os.listdir(LIC_DIR))
        st = process_pack(name, version, lic_done, force_license=force_lic)
        if st.get("failed"):
            errors.append(name)
            old = old_sources.get(name)
            if old is not None:
                log("  keeping previous files and manifest entry for %s" % name)
                states.append(reconstruct_state(old,
                                                files_by_source.get(name, []),
                                                level))
            continue
        new_states.append(st)

    if level == "die+opn" and new_states:
        escalate(new_states)
        for st in new_states:  # persist escalated state
            with open(os.path.join(STATE, st["name"] + ".json"), "w",
                      encoding="utf-8") as f:
                json.dump(st, f, indent=1)
    states.extend(new_states)

    size = svd_tree_size()
    log("svd tree size: %.1f MB" % (size / 1e6))
    if size > SIZE_BUDGET and level == "die":
        log("over budget, escalating dedupe key")
        escalate(states)
        level = "die+opn"
        with open(os.path.join(WORK, "dedupe_level"), "w",
                  encoding="utf-8") as f:
            f.write(level)

    m = build_manifest(states, level)
    log("manifest: %d files, %.1f MB" %
        (m["stats"]["total_files"], m["stats"]["total_bytes"] / 1e6))
    log("artifact downloads: %d" % DOWNLOADS[0])
    if errors:
        log("FAILED packs: %s" % ", ".join(errors))
        return 1
    log("done")
    return 0


def full_fetch(packs):
    # licenses already extracted in earlier runs
    lic_done = {}
    for fn in os.listdir(STATE):
        with open(os.path.join(STATE, fn), encoding="utf-8") as f:
            st = json.load(f)
        if st.get("license"):
            lic_done[st["version"]] = st["license"]

    states = []
    for name, version in packs:
        states.append(process_pack(name, version, lic_done))

    failed = [s["name"] for s in states if s.get("failed")]
    if failed:
        log("FAILED packs: %s" % ", ".join(failed))

    level_marker = os.path.join(WORK, "dedupe_level")
    dedupe_level = "die"
    if os.path.exists(level_marker):  # escalation already applied in a prior run
        with open(level_marker, encoding="utf-8") as f:
            dedupe_level = f.read().strip() or "die"
    size = svd_tree_size()
    log("svd tree size: %.1f MB" % (size / 1e6))
    if size > SIZE_BUDGET:
        log("over budget, escalating dedupe key")
        escalate(states)
        dedupe_level = "die+opn"
        with open(level_marker, "w", encoding="utf-8") as f:
            f.write(dedupe_level)
        for st in states:  # persist escalated state
            if not st.get("failed"):
                with open(os.path.join(STATE, st["name"] + ".json"), "w",
                          encoding="utf-8") as f:
                    json.dump(st, f, indent=1)
        size = svd_tree_size()
        log("svd tree size after escalation: %.1f MB" % (size / 1e6))

    m = build_manifest(states, dedupe_level)
    log("manifest: %d files, %.1f MB" %
        (m["stats"]["total_files"], m["stats"]["total_bytes"] / 1e6))
    invalid = [(s["name"], i) for s in states for i in s.get("invalid", [])]
    for name, i in invalid:
        log("invalid svd in %s: %s (%s)" % (name, i["device"], i["error"]))
    log("artifact downloads: %d" % DOWNLOADS[0])
    log("done")


def main():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(STATE, exist_ok=True)
    os.makedirs(PACKS, exist_ok=True)
    os.makedirs(SVD_BASE, exist_ok=True)

    pidx = os.path.join(WORK, "SiliconLabs.pidx")
    log("downloading pack index (metadata only)")
    if not http_get(PIDX_URL, pidx):
        sys.exit("cannot download pidx")
    try:
        packs = select_packs(pidx)
    except ET.ParseError as e:
        sys.exit("cannot parse pidx: %s" % e)
    log("selected %d packs" % len(packs))

    manifest = load_manifest()
    if manifest is not None:
        sys.exit(incremental_update(packs, manifest))

    log("no usable manifest.json, doing a full fetch")
    full_fetch(packs)


if __name__ == "__main__":
    main()
