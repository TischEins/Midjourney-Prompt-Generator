# TischEins Midjourney Prompt Generator

A free, offline Windows app that generates smart, category-aware Midjourney prompts with a single click.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Offline](https://img.shields.io/badge/Works-Offline-brightgreen)

---

## Features

- **20 categories** — Portrait, Fantasy, Sci-Fi, Horror, Food, Editorial Fashion, Cyberpunk, and more
- **Smart rules** — illustrative styles never get real camera lenses; photographic styles always do
- **Version selector** — `--v 5.2` through `--v 8.1`
- **Aspect ratio selector** — 9 common ratios including 16:9, 9:16, 2:3, and more
- **Copy to Clipboard** — one click, ready to paste into Midjourney
- **Blacklist** — lock out prompts you don't want to see again
- **Save as TXT** — save any prompt as a text file
- **100% offline** — no API, no internet connection required

---

## Installation

```bash
pip install customtkinter
python main.py
```

### Optional: render the TischEins logo

```bash
pip install cairosvg Pillow
```

---

## Build as Windows .exe

```bat
build.bat
```

The finished exe will be in `dist/TischEins_Prompt_Generator.exe`.

---

## Project structure

```
midjourney_generator/
├── main.py           # UI (CustomTkinter)
├── prompt_engine.py  # Generation logic, blacklist, compatibility rules
├── prompt_data.py    # All prompt building blocks (20 categories)
├── assets/
│   └── tischlogo.svg
├── requirements.txt
└── build.bat
```

---

## How it works

Each prompt is assembled from 7 randomly chosen building blocks:

`Subject` + `Style` + `Setting` + `Camera` + `Lighting` + `Mood` + `Detail` + `Parameters`

The engine applies compatibility rules before combining — for example, a fantasy painting style will never receive a real camera lens description, and a food photography style always uses appropriate macro/overhead cameras.

---

## Made by

[TischEins](https://tischeins.org/) — Made with ♥ | 100% Free
