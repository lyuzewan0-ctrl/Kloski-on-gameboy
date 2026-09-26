# Kloski on gameboy

**Eight levels. Two control modes. Help Cao Cao escape on the Game Boy.**

A Game Boy implementation of **Klotski**, written in assembly for RGBDS. This repository preserves the original course project and adds a redesigned technical report.

[Download the ROM](main.gb) · [Read the redesigned report](output/pdf/klotski-report-redesigned.pdf) · [Original report](report.pdf) · [Original presentation](Klotski.pptx)

<p align="center">
  <img src="docs/assets/original-board.png" width="270" alt="Example Klotski board from the original report, with Cao Cao in the center, the top-left block selected, and two empty cells at the bottom">
</p>

<p align="center"><em>This image illustrates the encoding example in the original report. It is not a screenshot of the supplied ROM's first level.</em></p>

## Overview

This team project was developed for the **Digital System and Computer Structure** course. Ten blocks of different sizes occupy a board with 4 columns and 5 rows. Use the two empty cells to rearrange the blocks and bring the largest, 2 × 2 block, Cao Cao, to the bottom-center exit.

- **Eight levels:** choose different starting layouts from the menu.
- **Selection and movement modes:** select a block, then slide it. Inverted colors identify the selected block.
- **Collision detection:** prevents overlapping blocks, movement through walls, and moves without enough free space.
- **On-screen counters:** the level appears at the upper left and the move count at the upper right.
- **Game Boy graphics:** background tiles render the board, a sprite acts as the menu pointer, and changed screen regions are updated during VBlank.

The repository is archived under the name **Kloski on gameboy**. The puzzle's standard name and the original report title use **Klotski on Game Boy**.

## Quick start

1. Download [`main.gb`](main.gb), the preserved original 32 KiB game ROM.
2. Open it in [Emulicious](https://emulicious.net/), the emulator used by the original project. Check the emulator's input settings for your keyboard mapping.
3. Use the direction pad to choose a level, then press **Game Boy A** to enter.
4. Select a block, press **A** to enter movement mode, and use the direction pad to slide it.
5. Press **A** to finish moving and select another block, or **B** to return to the menu. Re-entering a level resets it.

The included ROM is ready to use; rebuilding is optional.

### Controls

A and B below refer to **Game Boy buttons**, not the corresponding letters on a computer keyboard.

| Context | Direction pad | Game Boy A | Game Boy B |
| --- | --- | --- | --- |
| Level menu | Choose a level | Load the selected level | No assigned action |
| Selection mode | Select a block in that direction | Enter movement mode | Return to the menu |
| Movement mode | Slide the selected block | Finish moving and return to selection mode | Return to the menu |
| Victory screen | No assigned action | Return to the menu | No assigned action |

The original report records the following Emulicious mapping: **keyboard S → Game Boy A**, **keyboard A → Game Boy B**, and the arrow keys for directions. Your emulator version or custom settings may use a different mapping.

Actions trigger when a button is pressed; release and press it again to repeat an action. The win condition is checked in selection mode, so press **A** after moving Cao Cao to the exit to finish the move and trigger the check.

## Reports and original materials

| File | Contents |
| --- | --- |
| [`report.pdf`](report.pdf) | Original five-page English report, dated 2025-01-06, preserved unchanged |
| [`output/pdf/klotski-report-redesigned.pdf`](output/pdf/klotski-report-redesigned.pdf) | Eight-page redesigned edition with a cover, clickable contents, consistent typography, a controls table, a bit-encoding diagram, and a redrawn state machine |
| [`Klotski.pptx`](Klotski.pptx) | Original presentation, preserved unchanged |

The redesigned edition retains the authorship information, technical content of Sections 1–8, encoding example, and both original figures, with light edits for clarity. Notes based on comparison with the source code are explicitly labeled:

- The report's `level1` encoding example differs from the first level in the supplied `data.inc`. The redesigned edition preserves the original example and explains the difference.
- The mapping table attributed to `table.inc` in the original report is located in `data.inc` in this version.
- The source displays a victory screen before A returns the player to the menu; the updated controls description reflects this behavior.
- Levels use internal indices 0–7 and display numbers 1–8. The move count is stored in `stepCounterArray`.

## Build from source

Install the [official RGBDS toolchain](https://github.com/gbdev/rgbds/releases) and add `rgbasm`, `rgblink`, and `rgbfix` to your `PATH`. The project was successfully rebuilt with **RGBDS v1.0.4** during archival verification. The resulting ROM's SHA-256 hash **exactly matches** the original `main.gb` in this repository.

Run the following commands from the repository root. Outputs go into `build/` to preserve the original ROM and object file in the root directory.

**Windows PowerShell:**

```powershell
New-Item -ItemType Directory -Force build | Out-Null
rgbasm -o build/main.o main.asm
rgblink -o build/main.gb build/main.o
rgbfix -v -p 0 build/main.gb
```

**macOS / Linux, with RGBDS installed:**

```sh
mkdir -p build
rgbasm -o build/main.o main.asm
rgblink -o build/main.gb build/main.o
rgbfix -v -p 0 build/main.gb
```

Check that each command succeeds before running the next, then open `build/main.gb` in the emulator. The build was verified on Windows; the macOS / Linux commands use the same tool arguments.

The original [`compile.bat`](compile.bat) is also included. It accepts a source filename without its extension, for example `compile.bat main`, but overwrites the matching `main.o` and `main.gb`. Use the commands above to keep build outputs separate from the original files.

### Debugging in VS Code

The original [`.vscode/launch.json`](.vscode/launch.json) includes a `Launch in Emulicious` configuration using `emulicious-debugger` on port `58870`. Set up the corresponding VS Code debugger extension and Emulicious remote debugging separately; these tools are not bundled with the repository.

## Implementation

| Component | Location and responsibilities |
| --- | --- |
| State machine and input | `main.asm`: `stateTransition`, `readKeys`, and the menu, selection, movement, and victory loops |
| Block logic | `main.asm`: `chooseUp/Down/Left/Right`, corner-selection special cases, `moveUp/Down/Left/Right`, and `moveBlock` |
| Matrices and rendering | `main.asm`: `matricesToShadowSCRN`, `ByteDecoder`, `UnitDraw`, and selective screen updates |
| Tiles and levels | `data.inc`: backgrounds, tile patterns, eight levels, state and mapping tables, and WRAM variables |
| Hardware definitions | `hardware.inc`: Game Boy registers, addresses, and hardware constants |

The board is represented by a **7-row × 6-column matrix totaling 42 bytes**. The inner 5 × 4 area is playable, and the outer cells form the wall. Each byte's upper four bits encode the block type, bit 2 marks selection, and the lowest two bits identify the cell's position within a block.

The rendering pipeline is:

```text
Read input → Select / move and check collisions → Form newMatrix
           → Compare oldMatrix with newMatrix
           → Decode changed cells and update shadowSCRN
           → Update the background during VBlank using the affected region's height
```

## Repository layout

```text
.
├── main.asm                  Original assembly source
├── data.inc                  Original graphics, levels, and variable definitions
├── hardware.inc              Original hardware definitions
├── compile.bat               Original build script
├── main.gb                   Original game ROM
├── main.o                    Original object file
├── report.pdf                Original report
├── Klotski.pptx               Original presentation
├── .vscode/launch.json        Original debugger configuration
├── README.md                 Project documentation
├── docs/
│   ├── assets/               Two figures extracted from the original report
│   └── original-files.sha256 Checksums of the original files
├── output/pdf/
│   └── klotski-report-redesigned.pdf
└── tools/
    ├── build_report.py       Redesigned report generator
    └── requirements-report.txt
```

The archival additions consist of documentation, extracted figures, the report generator, and Git configuration. All nine original files are preserved byte for byte. `.gitattributes` disables automatic line-ending conversion for the original text files, and the [SHA-256 manifest](docs/original-files.sha256) can be used to verify their integrity. Local output directories `build/` and `tmp/` are excluded from version control.

## Regenerate the redesigned PDF

Python 3.10 or later is required. From the repository root, run:

```sh
python -m pip install -r tools/requirements-report.txt
python tools/build_report.py
```

The generator reads `report.pdf` without modifying it, extracts its two figures into `docs/assets/`, and writes `output/pdf/klotski-report-redesigned.pdf`. It prefers Arial / Consolas on Windows or DejaVu on Linux, falling back to standard PDF fonts if neither is available. Font differences can affect layout, so review the pagination after regenerating the report.

## Team and credits

**Zewan Lyu · Zeyan YIN · Weihan Li · Xiang Li**

Mathematics with Computer Science

Original report date: 2025-01-06

`hardware.inc` comes from [gbdev/hardware.inc](https://github.com/gbdev/hardware.inc) and retains its **CC0-1.0** notice in the file header. The remaining original project materials were supplied without a separate license. Archiving and documenting the project does not add or change their licensing terms.
