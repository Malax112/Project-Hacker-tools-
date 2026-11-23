import os
import socket
import tkinter as tk

VARS = [
    "ALLUSERSPROFILE", "APPDATA", "CD", "CLIENTNAME", "CMDCMDLINE",
    "CMDEXTVERSION", "COMMONPROGRAMFILES", "COMPUTERNAME", "COMSPEC",
    "DATE", "ERRORLEVEL", "HOMEDRIVE", "HOMEPATH", "HOMESHARE",
    "LOCALAPPDATA", "LOGONSERVER", "NUMBER_OF_PROCESSORS", "OS", "PATH",
    "PATHEXT", "PROCESSOR_ARCHITECTURE", "PROCESSOR_IDENTIFIER",
    "PROCESSOR_LEVEL", "PROCESSOR_REVISION", "PROGRAMDATA",
    "PROGRAMFILES", "PROMPT", "SESSIONNAME", "SYSTEMDRIVE",
    "SYSTEMROOT", "TEMP", "TIME", "USERDOMAIN", "USERNAME",
    "USERPROFILE", "WINDIR",
]


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "unknown"


def build_report():
    lines = []
    ip = get_local_ip()
    lines.append(f"IP: {ip}")
    lines.append("")
    for name in VARS:
        value = os.environ.get(name, "")
        if name == "CD":
            value = os.getcwd()
        elif name == "CMDCMDLINE":
            try:
                value = "python " + os.path.abspath(__file__)
            except NameError:
                value = "python <script>"
        if value.strip():
            lines.append(f"{name}: {value}")
    return "\n".join(lines)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Info Reader")
        self.geometry("640x520")
        self.resizable(False, False)
        self.configure(bg="#1c1c1c")

        tk.Label(self, text="Report", bg="#1c1c1c", fg="white",
                 font=("Segoe UI", 24, "bold")).pack(pady=(16, 2))

        frame_text = tk.Frame(self, bg="#252526",
                              highlightthickness=1, highlightbackground="#333")
        frame_text.pack(fill="both", expand=True, padx=16, pady=8)

        scrollbar = tk.Scrollbar(frame_text, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.output = tk.Text(frame_text, bg="#252526", fg="#e0e0e0",
                              font=("Consolas", 11), wrap="none", relief="flat",
                              yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.output.yview)
        self.output.configure(state="disabled")

        self.status = tk.Label(self, bg="#1c1c1c", fg="gray",
                               text="Ready", font=("Segoe UI", 12))
        self.status.pack(pady=6)

        self.show_report()

    def show_report(self):
        report_text = build_report()
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", report_text)
        self.output.configure(state="disabled")
        self.status.configure(text="Done", fg="#4ade80")


if __name__ == "__main__":
    app = App()
    app.mainloop()
