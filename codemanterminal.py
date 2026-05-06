import customtkinter as ctk
import os
import subprocess
import threading
import re

class TerminalApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CodeMan's Terminal")
        self.geometry("1000x650")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#000000")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Output Area
        self.output_text = ctk.CTkTextbox(
            self, font=("Consolas", 14), fg_color="#000000", 
            text_color="#ffffff", scrollbar_button_color="#333333", corner_radius=0
        )
        self.output_text.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.output_text.insert("0.0", "CodeMan Terminal [Version 1.4.1]\nChrome & Pip Management System\n\n")
        self.output_text.configure(state="disabled")

        # 2. Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", height=10, fg_color="#333333", progress_color="#ffffff")
        self.progress_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # 3. Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.input_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        self.prompt_label = ctk.CTkLabel(self.input_frame, text=f"{os.getcwd()}>", font=("Consolas", 14), text_color="#ffffff")
        self.prompt_label.grid(row=0, column=0, padx=(0, 5))

        self.command_entry = ctk.CTkEntry(self.input_frame, font=("Consolas", 14), border_width=0, fg_color="#000000", text_color="#ffffff")
        self.command_entry.grid(row=0, column=1, sticky="ew")
        self.command_entry._entry.configure(insertbackground="#ffffff")
        
        self.command_entry.bind("<Return>", self.process_command)
        self.command_entry.focus_set()

    def write_to_terminal(self, text):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", text + "\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")

    def execute_with_progress(self, full_command):
        def run():
            try:
                process = subprocess.Popen(
                    full_command, shell=True, stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, text=True, bufsize=1
                )
                
                for line in process.stdout:
                    self.after(0, lambda l=line: self.write_to_terminal(l.strip()))
                    if "%" in line:
                        match = re.search(r"(\d+)%", line)
                        if match:
                            val = int(match.group(1)) / 100
                            self.after(0, lambda v=val: self.progress_bar.set(v))
                
                process.wait()
                self.after(0, lambda: self.progress_bar.set(0))
            except Exception as e:
                self.after(0, lambda e=e: self.write_to_terminal(f"Error: {e}"))
        
        threading.Thread(target=run, daemon=True).start()

    def process_command(self, event):
        raw_input = self.command_entry.get().strip()
        self.command_entry.delete(0, "end")
        self.write_to_terminal(f"{os.getcwd()}> {raw_input}")
        
        if not raw_input: return

        # --- CHROME PROFILE LOGIC ---
        if "run chrome.exe load_user=" in raw_input:
            try:
                # Splitting to get profile and check for /y
                data = raw_input.split("load_user=")[1]
                if "/y" in data:
                    profile_id = data.split("/y")[0].strip()
                    self.write_to_terminal(f"Requesting Chrome Profile: {profile_id}...")
                    # Using start chrome --profile-directory
                    chrome_cmd = f'start chrome.exe --profile-directory="{profile_id}"'
                    subprocess.Popen(chrome_cmd, shell=True)
                else:
                    self.write_to_terminal("Error: Confirmation flag '/y' required to execute.")
            except Exception as e:
                self.write_to_terminal(f"Command Error: {e}")

        # --- PIP COMMANDS ---
        elif raw_input.lower().startswith("pip"):
            if "remove" in raw_input.lower():
                pkg = raw_input.lower().replace("pip remove", "").strip()
                self.execute_with_progress(f"pip uninstall {pkg} -y")
            else:
                self.execute_with_progress(raw_input)

        # --- BASIC NAV & SYSTEM ---
        elif raw_input.lower() == "cls":
            self.output_text.configure(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.configure(state="disabled")
        elif raw_input.lower() == "gopath..":
            os.chdir("..")
        elif raw_input.lower().startswith("gopath "):
            path = raw_input[7:].strip()
            if os.path.isdir(path): os.chdir(path)
            else: self.write_to_terminal(f"Directory not found: {path}")
        elif raw_input.lower() == "exit":
            self.destroy()
        else:
            self.execute_with_progress(raw_input)

        self.prompt_label.configure(text=f"{os.getcwd()}>")

if __name__ == "__main__":
    app = TerminalApp()
    app.mainloop()