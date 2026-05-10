# Calculator App

Simple calculator project with two versions:
- `calculator.py` - advanced CLI calculator
- `gui_calculator.py` - Windows-style GUI calculator (`tkinter`)

## Features

### GUI calculator
- Dark UI inspired by Windows Calculator
- Buttons: `C`, `CE`, `⌫`, `%`, `+/-`, `x²`, `√x`, `+ - × ÷`, `=`
- Keyboard support (`0-9`, `+ - * /`, `Enter`, `Backspace`, `Esc`)

### CLI calculator
- Safe expression parsing (AST, no direct `eval`)
- Variables (`x = 10`)
- Built-in constants (`pi`, `e`, `tau`)
- Built-in functions (`sqrt`, `sin`, `cos`, `log`, etc.)
- Memory commands (`M+`, `M-`, `MR`, `MC`)
- History (`history`, `clear_history`)

## Requirements

- Python 3.10+ (tested on Python 3.13)

## Run

From project folder:

```bash
python gui_calculator.py
```

CLI mode:

```bash
python calculator.py
```

## Build EXE (Windows)

### One command (recommended)

```cmd
build_exe.bat
```

After build, executable will be here:
- `dist\Calculator.exe`

### Manual way

```cmd
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name Calculator gui_calculator.py
```

## GitHub updates (quick flow)

```cmd
git add .
git commit -m "Update calculator"
git push
```

## Download

- [Download Calculator.exe (Windows)](https://github.com/lhereisemptyl/calculator-app/releases/download/v1.0.0/Calculator.exe)
