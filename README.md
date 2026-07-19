# Silicon Labs CMSIS SVD collection

CMSIS SVD register description files for Silicon Labs EFM32, EFR32, EZR32, WGM, xGM module, Series 3 (SIxG301) and SiWx917 devices. Extracted from the official Silicon Labs CMSIS packs at https://www.silabs.com/documents/public/cmsis-packs/. Snapshot taken 2026-07-19. One SVD file per die variant, 189 files standing in for 1260 orderable part numbers, about 959 MB.

## Layout

- `<FAMILY>/<DEVICE>.svd` register descriptions, family taken from the pack name
- `manifest.json` full file list with per-file source pack and `also_covers` part names
- `fetch.py` re-runs the whole fetch (Python 3 stdlib only)
- `LICENSES/` upstream license files as retrieved, plus extracts quoted below

## Sources

Pack index: https://www.silabs.com/documents/public/cmsis-packs/SiliconLabs.pidx (fetched 2026-07-19, index timestamp 2026-02-20).
Each pack was downloaded as `https://www.silabs.com/documents/public/cmsis-packs/SiliconLabs.<name>.<version>.pack`.

Selected packs: every `GeckoPlatform_*_DFP` (45 packs at 4.4.0 covering Series 0/1, 40 packs at 2025.12.1 covering Series 2 plus Series 3 SIBG301/SIMG301) and `Wiseconnect_SIWG917_DFP` 3.5.2. The 47 legacy packs at 5.8.10 (names without the `GeckoPlatform_` prefix) were skipped, they cover the same families and are superseded. The server publishes no checksums, the versions in the table pin the exact pack files. All 86 downloads succeeded.

## Coverage

Files is the number of SVD files kept, parts is the number of orderable part numbers those files stand in for (see dedupe below, full mapping in `manifest.json` under `also_covers`).

| Family | Pack | Version | Files | Parts |
|---|---|---|---|---|
| BGM1 | GeckoPlatform_BGM1_DFP | 4.4.0 | 8 | 9 |
| BGM13 | GeckoPlatform_BGM13_DFP | 4.4.0 | 2 | 8 |
| BGM21 | GeckoPlatform_BGM21_DFP | 2025.12.1 | 8 | 8 |
| BGM22 | GeckoPlatform_BGM22_DFP | 2025.12.1 | 6 | 6 |
| BGM24 | GeckoPlatform_BGM24_DFP | 2025.12.1 | 10 | 10 |
| BGM26 | GeckoPlatform_BGM26_DFP | 2025.12.1 | 2 | 2 |
| BGM27 | GeckoPlatform_BGM27_DFP | 2025.12.1 | 1 | 1 |
| EFM32G | GeckoPlatform_EFM32G_DFP | 4.4.0 | 1 | 32 |
| EFM32GG | GeckoPlatform_EFM32GG_DFP | 4.4.0 | 1 | 42 |
| EFM32GG11B | GeckoPlatform_EFM32GG11B_DFP | 4.4.0 | 1 | 60 |
| EFM32GG12B | GeckoPlatform_EFM32GG12B_DFP | 4.4.0 | 1 | 74 |
| EFM32HG | GeckoPlatform_EFM32HG_DFP | 4.4.0 | 1 | 20 |
| EFM32JG12B | GeckoPlatform_EFM32JG12B_DFP | 4.4.0 | 1 | 4 |
| EFM32JG1B | GeckoPlatform_EFM32JG1B_DFP | 4.4.0 | 1 | 9 |
| EFM32LG | GeckoPlatform_EFM32LG_DFP | 4.4.0 | 1 | 64 |
| EFM32PG12B | GeckoPlatform_EFM32PG12B_DFP | 4.4.0 | 1 | 4 |
| EFM32PG1B | GeckoPlatform_EFM32PG1B_DFP | 4.4.0 | 1 | 11 |
| EFM32PG22 | GeckoPlatform_EFM32PG22_DFP | 2025.12.1 | 1 | 8 |
| EFM32PG23 | GeckoPlatform_EFM32PG23_DFP | 2025.12.1 | 1 | 12 |
| EFM32PG26 | GeckoPlatform_EFM32PG26_DFP | 2025.12.1 | 1 | 12 |
| EFM32PG28 | GeckoPlatform_EFM32PG28_DFP | 2025.12.1 | 1 | 4 |
| EFM32TG | GeckoPlatform_EFM32TG_DFP | 4.4.0 | 1 | 35 |
| EFM32TG11B | GeckoPlatform_EFM32TG11B_DFP | 4.4.0 | 1 | 52 |
| EFM32WG | GeckoPlatform_EFM32WG_DFP | 4.4.0 | 1 | 64 |
| EFM32ZG | GeckoPlatform_EFM32ZG_DFP | 4.4.0 | 1 | 16 |
| EFR32BG12P | GeckoPlatform_EFR32BG12P_DFP | 4.4.0 | 1 | 17 |
| EFR32BG13P | GeckoPlatform_EFR32BG13P_DFP | 4.4.0 | 1 | 11 |
| EFR32BG1B | GeckoPlatform_EFR32BG1B_DFP | 4.4.0 | 1 | 17 |
| EFR32BG1P | GeckoPlatform_EFR32BG1P_DFP | 4.4.0 | 1 | 11 |
| EFR32BG1V | GeckoPlatform_EFR32BG1V_DFP | 4.4.0 | 1 | 7 |
| EFR32BG21 | GeckoPlatform_EFR32BG21_DFP | 2025.12.1 | 2 | 12 |
| EFR32BG22 | GeckoPlatform_EFR32BG22_DFP | 2025.12.1 | 3 | 13 |
| EFR32BG24 | GeckoPlatform_EFR32BG24_DFP | 2025.12.1 | 3 | 24 |
| EFR32BG26 | GeckoPlatform_EFR32BG26_DFP | 2025.12.1 | 1 | 18 |
| EFR32BG27 | GeckoPlatform_EFR32BG27_DFP | 2025.12.1 | 1 | 6 |
| EFR32BG29 | GeckoPlatform_EFR32BG29_DFP | 2025.12.1 | 1 | 4 |
| EFR32FG12P | GeckoPlatform_EFR32FG12P_DFP | 4.4.0 | 1 | 16 |
| EFR32FG13P | GeckoPlatform_EFR32FG13P_DFP | 4.4.0 | 1 | 7 |
| EFR32FG14P | GeckoPlatform_EFR32FG14P_DFP | 4.4.0 | 1 | 12 |
| EFR32FG14V | GeckoPlatform_EFR32FG14V_DFP | 4.4.0 | 1 | 2 |
| EFR32FG1P | GeckoPlatform_EFR32FG1P_DFP | 4.4.0 | 1 | 18 |
| EFR32FG1V | GeckoPlatform_EFR32FG1V_DFP | 4.4.0 | 1 | 20 |
| EFR32FG22 | GeckoPlatform_EFR32FG22_DFP | 2025.12.1 | 1 | 4 |
| EFR32FG23 | GeckoPlatform_EFR32FG23_DFP | 2025.12.1 | 3 | 23 |
| EFR32FG25 | GeckoPlatform_EFR32FG25_DFP | 2025.12.1 | 2 | 14 |
| EFR32FG28 | GeckoPlatform_EFR32FG28_DFP | 2025.12.1 | 2 | 18 |
| EFR32FG2D | GeckoPlatform_EFR32FG2D_DFP | 2025.12.1 | 2 | 6 |
| EFR32MG12P | GeckoPlatform_EFR32MG12P_DFP | 4.4.0 | 1 | 23 |
| EFR32MG13P | GeckoPlatform_EFR32MG13P_DFP | 4.4.0 | 1 | 12 |
| EFR32MG14P | GeckoPlatform_EFR32MG14P_DFP | 4.4.0 | 1 | 9 |
| EFR32MG1B | GeckoPlatform_EFR32MG1B_DFP | 4.4.0 | 1 | 15 |
| EFR32MG1P | GeckoPlatform_EFR32MG1P_DFP | 4.4.0 | 1 | 19 |
| EFR32MG1V | GeckoPlatform_EFR32MG1V_DFP | 4.4.0 | 1 | 4 |
| EFR32MG21 | GeckoPlatform_EFR32MG21_DFP | 2025.12.1 | 3 | 13 |
| EFR32MG22 | GeckoPlatform_EFR32MG22_DFP | 2025.12.1 | 3 | 6 |
| EFR32MG24 | GeckoPlatform_EFR32MG24_DFP | 2025.12.1 | 2 | 41 |
| EFR32MG26 | GeckoPlatform_EFR32MG26_DFP | 2025.12.1 | 1 | 25 |
| EFR32MG27 | GeckoPlatform_EFR32MG27_DFP | 2025.12.1 | 1 | 4 |
| EFR32MG29 | GeckoPlatform_EFR32MG29_DFP | 2025.12.1 | 1 | 2 |
| EFR32MR21 | GeckoPlatform_EFR32MR21_DFP | 2025.12.1 | 1 | 1 |
| EFR32SG23 | GeckoPlatform_EFR32SG23_DFP | 2025.12.1 | 1 | 2 |
| EFR32SG28 | GeckoPlatform_EFR32SG28_DFP | 2025.12.1 | 1 | 4 |
| EFR32ZG13L | GeckoPlatform_EFR32ZG13L_DFP | 4.4.0 | 1 | 2 |
| EFR32ZG13P | GeckoPlatform_EFR32ZG13P_DFP | 4.4.0 | 1 | 3 |
| EFR32ZG13S | GeckoPlatform_EFR32ZG13S_DFP | 4.4.0 | 1 | 1 |
| EFR32ZG14P | GeckoPlatform_EFR32ZG14P_DFP | 4.4.0 | 1 | 2 |
| EFR32ZG23 | GeckoPlatform_EFR32ZG23_DFP | 2025.12.1 | 2 | 10 |
| EFR32ZG28 | GeckoPlatform_EFR32ZG28_DFP | 2025.12.1 | 2 | 16 |
| EZR32HG | GeckoPlatform_EZR32HG_DFP | 4.4.0 | 1 | 28 |
| EZR32LG | GeckoPlatform_EZR32LG_DFP | 4.4.0 | 1 | 42 |
| EZR32WG | GeckoPlatform_EZR32WG_DFP | 4.4.0 | 1 | 42 |
| FGM23 | GeckoPlatform_FGM23_DFP | 2025.12.1 | 2 | 2 |
| MGM1 | GeckoPlatform_MGM1_DFP | 4.4.0 | 2 | 2 |
| MGM12 | GeckoPlatform_MGM12_DFP | 4.4.0 | 1 | 6 |
| MGM13 | GeckoPlatform_MGM13_DFP | 4.4.0 | 2 | 8 |
| MGM21 | GeckoPlatform_MGM21_DFP | 2025.12.1 | 11 | 11 |
| MGM22 | GeckoPlatform_MGM22_DFP | 2025.12.1 | 1 | 1 |
| MGM24 | GeckoPlatform_MGM24_DFP | 2025.12.1 | 15 | 15 |
| MGM26 | GeckoPlatform_MGM26_DFP | 2025.12.1 | 6 | 6 |
| MGM27 | GeckoPlatform_MGM27_DFP | 2025.12.1 | 2 | 2 |
| SIBG301 | GeckoPlatform_SIBG301_DFP | 2025.12.1 | 6 | 6 |
| SIMG301 | GeckoPlatform_SIMG301_DFP | 2025.12.1 | 11 | 11 |
| SIWG917 | Wiseconnect_SIWG917_DFP | 3.5.2 | 3 | 3 |
| WGM160 | GeckoPlatform_WGM160_DFP | 4.4.0 | 4 | 8 |
| ZGM13 | GeckoPlatform_ZGM13_DFP | 4.4.0 | 1 | 2 |
| ZGM23 | GeckoPlatform_ZGM23_DFP | 2025.12.1 | 4 | 4 |

## Dedupe rule

The packs ship one SVD (1 to 9 MB) per orderable part number. Parts that share a die have identical register maps, so extracting everything would be several GB of duplicates.

1. First pass: group filenames by die key, the device name up to the first `F<digits>` flash code (`EFR32MG24B220F1536IM48` -> `EFR32MG24B220`), keep the lexicographically last file of each group. Result: 480 files, 2373 MB, over the 1.2 GB budget.
2. Escalated pass: also strip trailing OPN digits from the die key (`EFR32MG24B220` -> `EFR32MG24B`), keep the lexicographically last file of each escalated group. Result: 189 files, 959 MB.

Every part name a kept file stands in for is listed in that file's `also_covers` entry in `manifest.json`. SIWG917, SIBG301 and SIMG301 part names carry no `F<digits>` code, so they are all kept as-is. Note the kept file is the largest flash variant, the flash size in a covered part's name may be smaller than what the kept file's memory map states.

## LICENSE & REDISTRIBUTION STATUS

Three regimes apply. Read this before redistributing.

1. Pack license (all 86 packs). Every pack's pdsc points to `License/license.md`, which is not a license text but a pointer to the Silicon Labs Master Software License Agreement (MSLA). Quoting the file (copies in `LICENSES/*-license.md`): "The licensor of this software is Silicon Laboratories Inc. Your use of this software is governed by the terms of Silicon Labs Master Software License Agreement (MSLA) available at www.silabs.com/about-us/legal/master-software-license-agreement." The MSLA (plain text extract in `LICENSES/SiliconLabs-MSLA-web-extract.txt`, retrieved 2026-07-19) is a proprietary agreement, not an open source license. It grants "a limited, non-transferable, non-exclusive, perpetual license" and only allows distributing derivative works "to Authorized Subcontractors".

2. Series 0/1 SVD files (58 files, the 45 packs at 4.4.0): each file embeds the Zlib license in its `<licenseText>` element, including "SPDX-License-Identifier: Zlib" and the full Zlib text ("Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely..."). Copy in `LICENSES/SVD-embedded-Zlib-header.txt`. These files are redistributable under Zlib. This confirms the expected Zlib licensing, but only for this generation.

3. SIWG917 SVD files (3 files): each embeds an ARM notice stating "This file can be freely distributed. Modifications to this file shall be clearly marked." Copy in `LICENSES/SVD-embedded-ARM-header.txt`. Redistributable per that notice.

WARNING: the 128 files from the 40 packs at 2025.12.1 (Series 2, SIBG301, SIMG301) contain NO license text at all. For them only the pack-level MSLA applies, and the MSLA is not a permissive license. Public redistribution of these 128 files is not clearly permitted. Treat them as MSLA-licensed vendor files: fine for internal development use with Silicon Labs devices, get legal advice before republishing.

## Provenance

All 189 files are `pristine`: extracted byte-for-byte from the vendor packs, no edits. Legend used in `manifest.json`: `pristine` (unmodified vendor file), `patched` (vendor file with local fixes), `community` (third-party authored), `converted` (generated from another format). Only `pristine` occurs here.

## Refresh

    python fetch.py

Stdlib only, no dependencies. The script downloads the pidx, re-selects packs by the same name rules, downloads and processes one pack at a time and deletes each pack archive after extraction. It keeps per-pack state in `.work/state/`, so it can be interrupted and re-run, finished packs are skipped. A fresh run downloads about 1.7 GB and needs about 2.4 GB of transient disk before the dedupe escalation kicks in. Delete `.work/` when it is done.

The fetch is incremental: it first compares upstream pack versions from the pidx against `manifest.json` and downloads only the packs that changed, so a run with no upstream changes downloads nothing and leaves the tree untouched (deleting `manifest.json` forces the full fetch described above). A GitHub Action (`.github/workflows/check-updates.yml`) runs the script weekly on Monday at 06:00 UTC and commits any updates.

## Known gaps and issues

- The 128 Series 2/3 files have no embedded license, see the warning above.
- Only one SVD per die group is kept. Covered parts with smaller flash share the kept file, whose memory map states the largest flash size.
- The legacy 5.8.10 packs were not used. Their families are all covered by the GeckoPlatform packs.
- EFM8 and other 8051 parts have no SVDs (not Cortex-M, not in scope of CMSIS packs).
- All extracted files passed XML validation (well-formed, root element `device`). Zero failures, zero invalid files, zero download failures.
