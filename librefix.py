"""
LibreFix - Fix FreeStyle Libre Bluetooth on Fairphone after Android 15 update
https://github.com/108111/librefix

Based on research by Wanna_Winn (Fairphone Community Forum)
Developed with Claude AI (Anthropic)
"""

import tkinter as tk
import subprocess
import threading
import os
import sys
import tempfile
import base64
import shutil

try:
    from adb_bundle import ADB_EXE, ADBWINAPI_DLL, ADBWINUSBAPI_DLL
    BUNDLED_ADB = True
except ImportError:
    BUNDLED_ADB = False

LIBRELINK_PACKAGES = [
    "com.freestylelibre.app.gb",
    "com.freestylelibre.app.fr",
    "com.freestylelibre.app.de",
    "com.freestylelibre.app.us",
    "com.freestylelibre.app.nl",
    "com.freestylelibre.app.be",
    "com.freestylelibre.app.es",
    "com.freestylelibre.app.it",
    "com.freestylelibre.app.se",
    "com.freestylelibre.app.no",
    "com.freestylelibre.app.dk",
    "com.freestylelibre.app.fi",
    "com.freestylelibre.app.au",
    "com.freestylelibre.app.ca",
    "com.abbott.librelink",
]

TMP_DIR = None
CREATE_NO_WINDOW = 0x08000000


def get_adb_path():
    global TMP_DIR
    if BUNDLED_ADB:
        if TMP_DIR is None:
            TMP_DIR = tempfile.mkdtemp(prefix="librefix_")
            adb_path = os.path.join(TMP_DIR, "adb.exe")
            with open(adb_path, "wb") as f:
                f.write(base64.b64decode(ADB_EXE))
            for name, data in [
                ("AdbWinApi.dll", ADBWINAPI_DLL),
                ("AdbWinUsbApi.dll", ADBWINUSBAPI_DLL)
            ]:
                with open(os.path.join(TMP_DIR, name), "wb") as f:
                    f.write(base64.b64decode(data))
        return os.path.join(TMP_DIR, "adb.exe")
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    for name in ["adb.exe", "adb"]:
        path = os.path.join(script_dir, name)
        if os.path.exists(path):
            return path
    return "adb"


def run_adb(args):
    adb = get_adb_path()
    try:
        result = subprocess.run(
            [adb] + args,
            capture_output=True, text=True, timeout=15,
            creationflags=CREATE_NO_WINDOW
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timed out", 1
    except FileNotFoundError:
        return "", "ADB not found", 1


def check_device():
    stdout, _, _ = run_adb(["devices"])
    lines = stdout.strip().split('\n')
    if any('unauthorized' in l for l in lines[1:]):
        return "unauthorized"
    if any('\tdevice' in l for l in lines[1:]):
        return "connected"
    return "none"


def detect_package():
    stdout, _, code = run_adb(["shell", "pm", "list", "packages"])
    if code != 0:
        return None
    for pkg in LIBRELINK_PACKAGES:
        if pkg.lower() in stdout.lower():
            return pkg
    return None


def apply_fix(package, progress_cb):
    commands = [
        (["shell", "settings", "put", "global", "ble_scan_always_enabled", "1"],
         "Enabling BLE scanning"),
        (["shell", "cmd", "bluetooth_manager", "enable"],
         "Enabling Bluetooth manager"),
        (["shell", "pm", "grant", package, "android.permission.BLUETOOTH_CONNECT"],
         "Granting Bluetooth permission (1/3)"),
        (["shell", "pm", "grant", package, "android.permission.BLUETOOTH_SCAN"],
         "Granting Bluetooth permission (2/3)"),
        (["shell", "pm", "grant", package, "android.permission.BLUETOOTH_ADVERTISE"],
         "Granting Bluetooth permission (3/3)"),
        (["shell", "pm", "grant", package, "android.permission.ACCESS_FINE_LOCATION"],
         "Granting location permission"),
        (["shell", "pm", "grant", package, "android.permission.ACCESS_COARSE_LOCATION"],
         "Granting coarse location permission"),
        (["shell", "pm", "grant", package, "android.permission.POST_NOTIFICATIONS"],
         "Granting notification permission"),
        (["shell", "cmd", "appops", "set", "com.android.bluetooth",
          "RUN_IN_BACKGROUND", "allow"],
         "Protecting Bluetooth system service"),
        (["shell", "cmd", "appops", "set", package, "RUN_IN_BACKGROUND", "allow"],
         "Allowing LibreLink background access (1/2)"),
        (["shell", "cmd", "appops", "set", package, "RUN_ANY_IN_BACKGROUND", "allow"],
         "Allowing LibreLink background access (2/2)"),
        (["shell", "dumpsys", "deviceidle", "whitelist", f"+{package}"],
         "Whitelisting from battery optimisation"),
        (["shell", "cmd", "netpolicy", "add", "restrict-background-whitelist", package],
         "Removing network restrictions"),
        (["shell", "am", "force-stop", package],
         "Restarting LibreLink"),
    ]
    total = len(commands)
    for i, (args, desc) in enumerate(commands):
        progress_cb(i, total, desc)
        run_adb(args)
    progress_cb(total, total, "Complete")


# ── Colours ───────────────────────────────────────────────────────────────────
BG      = "#0f1117"
CARD    = "#1c1f2e"
ACCENT  = "#00d4ff"
SUCCESS = "#00e676"
WARNING = "#ffab00"
ERROR   = "#ff5252"
TEXT    = "#e0e0e0"
SUB     = "#777777"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("LibreFix")
        self.root.geometry("500x640")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.fixing = False
        self.page = None
        self._build_setup()

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _header(self):
        tk.Label(self.root, text="LibreFix",
                 font=("Helvetica", 30, "bold"),
                 fg=ACCENT, bg=BG, pady=18).pack()
        tk.Label(self.root,
                 text="Restore FreeStyle Libre Bluetooth on Fairphone",
                 font=("Helvetica", 11), fg=SUB, bg=BG).pack()
        tk.Frame(self.root, bg="#2a2d3e", height=1).pack(
            fill=tk.X, padx=20, pady=14)

    def _footer(self):
        tk.Label(self.root,
                 text="Research: Wanna_Winn (Fairphone Forum)  |  Built with Claude AI (Anthropic)",
                 font=("Helvetica", 7), fg="#333333", bg=BG,
                 pady=8).pack(side=tk.BOTTOM)

    # ── Page 1: Setup instructions ────────────────────────────────────────────
    def _build_setup(self):
        self._clear()
        self.page = "setup"

        self._header()

        tk.Label(self.root,
                 text="Step 1 of 2 - Enable USB Debugging on your phone",
                 font=("Helvetica", 11, "bold"), fg=TEXT, bg=BG).pack(padx=20)

        tk.Label(self.root,
                 text="This lets LibreFix talk to your phone.\n"
                      "It is safe and you can turn it off afterwards.",
                 font=("Helvetica", 10), fg=SUB, bg=BG,
                 justify=tk.CENTER).pack(pady=6)

        tk.Frame(self.root, bg="#2a2d3e", height=1).pack(
            fill=tk.X, padx=20, pady=8)

        steps = [
            ("1", "On your phone, open Settings"),
            ("2", "Tap About Phone"),
            ("3", "Find Build Number and tap it 7 times\n     You'll see 'You are now a developer'"),
            ("4", "Go back to Settings"),
            ("5", "Tap System, then Developer Options"),
            ("6", "Turn on USB Debugging"),
            ("7", "Connect your phone to this computer\n     using a USB data cable"),
            ("8", "Tap Allow on the popup that appears\n     on your phone screen"),
        ]

        wrap = tk.Frame(self.root, bg=BG, padx=30)
        wrap.pack(fill=tk.X)

        for num, text in steps:
            row = tk.Frame(wrap, bg=BG, pady=2)
            row.pack(fill=tk.X)
            tk.Label(row, text=num + ".",
                     font=("Helvetica", 10, "bold"),
                     fg=ACCENT, bg=BG, width=3, anchor=tk.NE).pack(side=tk.LEFT)
            tk.Label(row, text=text,
                     font=("Helvetica", 10),
                     fg=TEXT, bg=BG, anchor=tk.W,
                     justify=tk.LEFT).pack(side=tk.LEFT, padx=6)

        tk.Frame(self.root, bg="#2a2d3e", height=1).pack(
            fill=tk.X, padx=20, pady=12)

        tk.Button(self.root,
                  text="Done - Fix My Libre  ->",
                  font=("Helvetica", 14, "bold"),
                  bg=ACCENT, fg="#000000",
                  padx=30, pady=10,
                  relief=tk.FLAT, cursor="hand2",
                  command=self._build_fix).pack()

        self._footer()

    # ── Page 2: Fix ───────────────────────────────────────────────────────────
    def _build_fix(self):
        self._clear()
        self.page = "fix"
        self.fixing = False

        self._header()

        tk.Label(self.root,
                 text="Step 2 of 2 - Fix your Libre",
                 font=("Helvetica", 11, "bold"), fg=TEXT, bg=BG).pack(padx=20)

        tk.Label(self.root,
                 text="Make sure your phone is plugged in and you tapped Allow.",
                 font=("Helvetica", 10), fg=SUB, bg=BG).pack(pady=4)

        tk.Frame(self.root, bg="#2a2d3e", height=1).pack(
            fill=tk.X, padx=20, pady=12)

        # Status row
        sf = tk.Frame(self.root, bg=BG, padx=24)
        sf.pack(fill=tk.X)
        self.dot = tk.Label(sf, text="●", font=("Helvetica", 13),
                            fg=WARNING, bg=BG)
        self.dot.pack(side=tk.LEFT)
        self.status = tk.Label(sf, text="Checking for phone...",
                               font=("Helvetica", 10), fg=TEXT, bg=BG)
        self.status.pack(side=tk.LEFT, padx=8)

        # Progress bar
        pf = tk.Frame(self.root, bg=BG, padx=24, pady=6)
        pf.pack(fill=tk.X)
        pb_bg = tk.Frame(pf, bg="#2a2d3e", height=5)
        pb_bg.pack(fill=tk.X)
        self.pb = tk.Frame(pb_bg, bg=ACCENT, height=5, width=0)
        self.pb.place(x=0, y=0, relheight=1)
        self.pb_lbl = tk.Label(self.root, text="",
                               font=("Helvetica", 8), fg=SUB, bg=BG)
        self.pb_lbl.pack()

        # Button
        bf = tk.Frame(self.root, bg=BG, pady=14)
        bf.pack()
        self.btn = tk.Button(bf,
                             text="Fix My Libre  ->",
                             font=("Helvetica", 15, "bold"),
                             bg="#2a2d3e", fg=SUB,
                             padx=38, pady=13,
                             relief=tk.FLAT, cursor="hand2",
                             state=tk.DISABLED,
                             command=self._fix)
        self.btn.pack()
        self.btn_sub = tk.Label(bf, text="Waiting for phone...",
                                font=("Helvetica", 9), fg=SUB, bg=BG)
        self.btn_sub.pack(pady=3)

        # Result
        self.result = tk.Label(self.root, text="",
                               font=("Helvetica", 10), fg=TEXT, bg=BG,
                               justify=tk.LEFT, wraplength=440)
        self.result.pack(padx=24, fill=tk.X)

        # Back link
        back = tk.Label(self.root,
                        text="< Back to setup instructions",
                        font=("Helvetica", 9), fg=SUB, bg=BG, cursor="hand2")
        back.pack(pady=6)
        back.bind("<Button-1>", lambda e: self._build_setup())

        self._footer()
        self._poll()

    def _poll(self):
        if self.page != "fix" or self.fixing:
            return
        state = check_device()
        if state == "connected":
            self.dot.configure(fg=SUCCESS)
            self.status.configure(text="Phone connected!", fg=SUCCESS)
            self.btn.configure(state=tk.NORMAL, bg=ACCENT, fg="#000000",
                               text="Fix My Libre  ->")
            self.btn_sub.configure(text="Ready")
        elif state == "unauthorized":
            self.dot.configure(fg=WARNING)
            self.status.configure(
                text="Check your phone - tap Allow on the popup", fg=WARNING)
            self.btn.configure(state=tk.DISABLED, bg="#2a2d3e", fg=SUB)
            self.btn_sub.configure(text="Waiting for permission...")
        else:
            self.dot.configure(fg=WARNING)
            self.status.configure(
                text="Phone not found - is it plugged in?", fg=SUB)
            self.btn.configure(state=tk.DISABLED, bg="#2a2d3e", fg=SUB)
            self.btn_sub.configure(text="Connect your phone first")
        self.root.after(2000, self._poll)

    def _set_progress(self, cur, tot, lbl=""):
        try:
            w = int((cur / tot) * 452) if tot else 0
            self.pb.place(x=0, y=0, relheight=1, width=w)
            self.pb_lbl.configure(text=lbl)
        except Exception:
            pass

    def _fix(self):
        if self.fixing:
            return
        self.fixing = True
        self.btn.configure(state=tk.DISABLED, text="Fixing...",
                           bg="#2a2d3e", fg=SUB)
        self.result.configure(text="")
        threading.Thread(target=self._do_fix, daemon=True).start()

    def _do_fix(self):
        def upd(cur, tot, lbl):
            self.root.after(0, self._set_progress, cur, tot, lbl)

        upd(0, 14, "Detecting LibreLink...")
        pkg = detect_package()
        if not pkg:
            self.root.after(0, self._failed,
                            "LibreLink not found on your phone.\n"
                            "Please install it from the Play Store first.")
            return
        apply_fix(pkg, upd)
        self.root.after(0, self._done)

    def _done(self):
        self.fixing = False
        self.dot.configure(fg=SUCCESS)
        self.status.configure(text="Fix applied!", fg=SUCCESS)
        self._set_progress(14, 14, "Complete")
        self.btn.configure(state=tk.NORMAL, text="Run Again",
                           bg="#2a2d3e", fg=SUB)
        self.btn_sub.configure(text="")
        self.result.configure(
            fg=TEXT,
            text=(
                "Done!\n\n"
                "Open LibreLink on your phone and wait 2-3 minutes.\n"
                "It should show live readings instead of 'Ready to scan'.\n\n"
                "Important: Do not accept Fairphone software updates\n"
                "until Fairphone officially fixes the Bluetooth bug."
            )
        )

    def _failed(self, msg):
        self.fixing = False
        self.dot.configure(fg=ERROR)
        self.status.configure(text="Something went wrong", fg=ERROR)
        self.btn.configure(state=tk.NORMAL, text="Try Again",
                           bg=ACCENT, fg="#000000")
        self.result.configure(fg=ERROR, text=f"Error: {msg}")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
    if TMP_DIR and os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
