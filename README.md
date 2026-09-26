# Kloski on gameboy

**在 Game Boy 上实现华容道：八个关卡、两种操作模式，以及一次曹操逃脱。**

A Game Boy implementation of **Klotski**, written in assembly for RGBDS. This repository preserves the original course project and adds a redesigned technical report.

[下载游戏 ROM](main.gb) · [阅读美化版报告](output/pdf/klotski-report-redesigned.pdf) · [原始报告](report.pdf) · [原始演示文稿](Klotski.pptx)

<p align="center">
  <img src="docs/assets/original-board.png" width="270" alt="原报告中的华容道棋盘示例：曹操位于中央，上方左侧方块被选中，下方有两个空格">
</p>

<p align="center"><em>图片提取自原始报告，展示其编码示例，并非当前 ROM 第一关的截图。</em></p>

## 项目简介

这是 **Digital System and Computer Structure** 课程的团队项目。游戏在 4 列 × 5 行棋盘上放置十个大小不同的方块，玩家利用两个空格移动方块，让最大的 2 × 2 方块「曹操」抵达底部中央出口。

- **八个关卡**：通过菜单选择不同的初始布局。
- **选择 / 移动双模式**：先选择方块，再移动方块，选中状态通过反色显示。
- **碰撞检测**：阻止重叠、越界及空间不足的移动。
- **状态显示**：左上角显示关卡，右上角显示移动步数。
- **面向 Game Boy 的绘图实现**：棋盘使用背景图块，菜单指针使用精灵；在 VBlank 期间按变化区域更新画面。

仓库名称按项目归档要求使用 **Kloski on gameboy**；游戏的标准名称及原报告标题使用 **Klotski on Game Boy**。

## 快速开始

1. 下载仓库中的 [`main.gb`](main.gb)，这是保留的原始 32 KiB 游戏 ROM。
2. 使用 [Emulicious](https://emulicious.net/) 打开 ROM。原项目采用此模拟器；键位请以模拟器的输入设置为准。
3. 在菜单用方向键选关，按 **Game Boy A** 进入。
4. 选择方块，按 **A** 切换到移动模式，再用方向键滑动。
5. 按 **A** 完成移动、重新选择方块；按 **B** 返回菜单。重新进入关卡会重置该关。

不需要重新编译即可使用原始 ROM。

### 操作说明

这里的 A、B 均指 **Game Boy 按钮**，而不是电脑键盘上的同名按键。

| 场景 | 方向键 | Game Boy A | Game Boy B |
| --- | --- | --- | --- |
| 关卡菜单 | 选择关卡 | 进入关卡 | 无指定功能 |
| 选择模式 | 选择该方向的方块 | 进入移动模式 | 返回菜单 |
| 移动模式 | 移动选中的方块 | 完成移动，回到选择模式 | 返回菜单 |
| 胜利画面 | 无指定功能 | 返回菜单 | 无指定功能 |

原报告记录的 Emulicious 键位是：**键盘 S → Game Boy A，键盘 A → Game Boy B**；四个方向使用箭头键。不同版本或自定义配置可能不同。

输入按“按下”触发；连续操作时请松开后再次按键。胜利判断发生在选择模式，因此将曹操移到出口后，按 **A** 结束移动，以进入胜利判断。

## 报告与原始资料

| 文件 | 内容 |
| --- | --- |
| [`report.pdf`](report.pdf) | 原始英文报告，2025-01-06，共 5 页，保持原样 |
| [`output/pdf/klotski-report-redesigned.pdf`](output/pdf/klotski-report-redesigned.pdf) | 新增的 8 页美化版：封面、可点击目录、统一排版、按键表、位编码图与重绘的状态机 |
| [`Klotski.pptx`](Klotski.pptx) | 原始演示文稿，保持原样 |

美化版保留原报告的作者信息、1–8 节技术内容、编码示例和两幅原始图片，并整理英文表达。核对代码后补充的说明均有标注：

- 原报告的 `level1` 编码示例与当前 `data.inc` 的第一关不同；美化版保留原示例并注明差异。
- 原报告引用的 `table.inc` 在此版本中对应 `data.inc` 内的映射表。
- 原代码先显示胜利画面，再由 A 返回菜单；美化版按此说明操作。
- 关卡内部索引为 0–7，显示编号为 1–8；步数实际保存在 `stepCounterArray`。

## 从源码编译

使用 [RGBDS 官方工具链](https://github.com/gbdev/rgbds/releases)，将 `rgbasm`、`rgblink`、`rgbfix` 加入 `PATH`。本次已使用 **RGBDS v1.0.4** 成功编译，生成 ROM 的 SHA-256 与仓库原始 `main.gb` **完全一致**。

在仓库根目录运行以下命令，输出放入 `build/`，以保留根目录的原始 ROM 和目标文件。

**Windows PowerShell：**

```powershell
New-Item -ItemType Directory -Force build | Out-Null
rgbasm -o build/main.o main.asm
rgblink -o build/main.gb build/main.o
rgbfix -v -p 0 build/main.gb
```

**macOS / Linux（已安装 RGBDS）：**

```sh
mkdir -p build
rgbasm -o build/main.o main.asm
rgblink -o build/main.gb build/main.o
rgbfix -v -p 0 build/main.gb
```

每条命令成功后再执行下一条，然后在模拟器中打开 `build/main.gb`。本次验证环境为 Windows；以上 macOS / Linux 命令使用相同的工具参数。

原始 [`compile.bat`](compile.bat) 也保留在仓库中。它接受不带扩展名的源文件名，例如 `compile.bat main`，但会覆盖同名的 `main.o` 和 `main.gb`；为保留原始产物，建议使用上述独立输出目录的命令。

### VS Code 调试

原始 [`.vscode/launch.json`](.vscode/launch.json) 提供 `Launch in Emulicious` 配置，使用 `emulicious-debugger`，端口为 `58870`。使用时需要另行配置相应的 VS Code 调试扩展与 Emulicious 远程调试功能；这些工具不随仓库分发。

## 实现结构

| 部分 | 位置与职责 |
| --- | --- |
| 状态机与输入 | `main.asm`：`stateTransition`、`readKeys` 及菜单、选择、移动、胜利循环 |
| 方块逻辑 | `main.asm`：`chooseUp/Down/Left/Right`、角落选择特例、`moveUp/Down/Left/Right`、`moveBlock` |
| 矩阵与绘图 | `main.asm`：`matricesToShadowSCRN`、`ByteDecoder`、`UnitDraw` 与局部屏幕更新 |
| 图块与关卡 | `data.inc`：背景、图块图案、八个关卡、状态表、映射表与 WRAM 变量 |
| 硬件定义 | `hardware.inc`：Game Boy 寄存器、地址与硬件常量 |

棋盘由 **7 行 × 6 列，共 42 字节**的矩阵表示：内层 5 × 4 为可玩区域，外层为墙。每个字节的高四位表示方块类型，bit 2 表示是否选中，低两位表示该格在方块中的位置。

绘图流程为：

```text
读取按键 → 选择 / 移动与碰撞检测 → 形成 newMatrix
        → 比较 oldMatrix 与 newMatrix
        → 解码变化的单元，更新 shadowSCRN
        → 根据受影响区域高度，在 VBlank 期间更新背景
```

## 文件目录

```text
.
├── main.asm                 原始汇编代码
├── data.inc                 原始图形、关卡和变量定义
├── hardware.inc             原始硬件定义
├── compile.bat              原始编译脚本
├── main.gb                  原始游戏 ROM
├── main.o                   原始目标文件
├── report.pdf               原始报告
├── Klotski.pptx              原始演示文稿
├── .vscode/launch.json       原始调试配置
├── README.md                项目说明
├── docs/
│   ├── assets/              从原报告提取的两幅图片
│   └── original-files.sha256 原始文件校验清单
├── output/pdf/
│   └── klotski-report-redesigned.pdf
└── tools/
    ├── build_report.py      美化版报告生成器
    └── requirements-report.txt
```

本次整理仅新增文档、图片、报告生成器与 Git 配置。原始九个文件均按字节保留；`.gitattributes` 禁止对原始文本文件自动转换换行符。[SHA-256 清单](docs/original-files.sha256) 可用于检查归档完整性。`build/` 与 `tmp/` 是本地生成目录，不上传到仓库。

## 重新生成美化版 PDF

需要 Python 3.10 或更高版本。在仓库根目录执行：

```sh
python -m pip install -r tools/requirements-report.txt
python tools/build_report.py
```

生成器只读取 `report.pdf`，提取两幅原图至 `docs/assets/`，并写入 `output/pdf/klotski-report-redesigned.pdf`。优先使用 Windows Arial / Consolas 或 Linux DejaVu 字体，找不到时使用 PDF 标准字体。字体差异可能影响排版，重新生成后应检查分页。

## 团队与署名

**Zewan Lyu · Zeyan YIN · Weihan Li · Xiang Li**

Mathematics with Computer Science

原报告日期：2025-01-06

`hardware.inc` 源自 [gbdev/hardware.inc](https://github.com/gbdev/hardware.inc)，文件头保留其 **CC0-1.0** 声明。项目其余原始材料未附独立许可证，本次整理不新增或变更其许可条款。
