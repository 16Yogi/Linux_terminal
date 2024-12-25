import tkinter as tk
import os
import subprocess
import time

class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Linux Terminal")
        self.root.geometry("600x400")

        # Text widget for displaying terminal content
        # Set font to "Times New Roman", bold weight, and size 12
        self.text_area = tk.Text(root, bg="black", fg="white", font=("Times New Roman", 12, 'bold'), wrap=tk.WORD, spacing1=2)
        self.text_area.pack(expand=True, fill=tk.BOTH)

        # Set the prompt (default), and color $ symbol green
        self.text_area.insert(tk.END, "$: ")
        self.text_area.tag_configure("green", foreground="green")
        self.text_area.tag_add("green", "1.0", "1.1")

        # Change the cursor color to white
        self.text_area.config(insertbackground="white")  # Set cursor color to white

        # Bind the 'Return' key to process commands
        self.text_area.bind("<Return>", self.on_enter)

        # Bind the backspace key to handle it specifically
        self.text_area.bind("<BackSpace>", self.on_backspace)

        self.current_directory = os.getcwd()  # Track current directory

    def run(self):
        self.root.mainloop()

    def on_enter(self, event):
        # Get the input text and remove the last prompt
        input_text = self.get_input()
        self.text_area.delete(f"{self.text_area.index(tk.END).split('.')[0]}.0", tk.END)
        self.text_area.insert(tk.END, "\n")  # Move to the next line

        # Process the command
        output = self.process_input(input_text)

        # Show the output
        self.text_area.insert(tk.END, output)

        # Insert prompt again after output, making the $ symbol green
        self.text_area.insert(tk.END, "$: ")
        self.text_area.tag_add("green", f"{self.text_area.index(tk.END).split('.')[0]}.0", f"{self.text_area.index(tk.END).split('.')[0]}.2")

        # Move the cursor to the position right after the prompt ($)
        self.text_area.mark_set(tk.INSERT, f"{self.text_area.index(tk.END).split('.')[0]}.1")

        # Move the cursor to the end of the text area
        self.text_area.yview(tk.END)

    def get_input(self):
        # Get the last line of the text_area (user input)
        input_text = self.text_area.get("1.0", tk.END).strip().split("\n")[-1]
        return input_text

    def process_input(self, input_text):
        # Process the command and return the output
        if input_text == "exit":
            self.root.quit()
            return "Exiting terminal.\n"

        if input_text == "clear":
            self.clear_terminal()
            return ""  # No output, just clear the terminal

        if input_text.startswith("echo "):
            return self.echo(input_text[5:])

        if input_text.startswith("cd "):
            return self.change_directory(input_text[3:])

        if input_text.startswith("mkdir "):
            return self.create_directory(input_text[6:])

        if input_text == "ls":
            return self.list_directory()

        if input_text.startswith("shutdown"):
            return self.shutdown_system(input_text)

        if input_text.startswith("reboot"):
            return self.reboot_system()

        if input_text.startswith("sleep"):
            return self.sleep_system(input_text)

        if input_text == "cal":
            return self.show_calendar()

        if input_text == "calculator":
            return self.open_calculator()

        if input_text == "notepad":
            return self.open_notepad()

        # Run a system command if none of the above
        return self.run_system_command(input_text)

    def echo(self, text):
        return text + "\n"

    def change_directory(self, path):
        try:
            os.chdir(path)
            self.current_directory = os.getcwd()
            return f"Changed directory to {self.current_directory}\n"
        except FileNotFoundError:
            return f"Directory '{path}' not found.\n"
        except PermissionError:
            return f"Permission denied: '{path}'\n"

    def create_directory(self, directory_name):
        try:
            os.mkdir(directory_name)
            return f"Directory '{directory_name}' created.\n"
        except FileExistsError:
            return f"Directory '{directory_name}' already exists.\n"
        except PermissionError:
            return f"Permission denied to create directory '{directory_name}'\n"

    def list_directory(self):
        try:
            files = os.listdir(self.current_directory)
            return "\n".join(files) + "\n"
        except PermissionError:
            return f"Permission denied: {self.current_directory}\n"

    def run_system_command(self, command):
        try:
            # Check if the command is to open an application
            if command.startswith("open "):
                app_name = command[5:].strip()
                return self.open_application(app_name)

            # Else, run the command as a system command
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"Error: {e}\n"

    def open_application(self, app_name):
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen([app_name])  # Just type the app name if it's in PATH
                return f"Opening {app_name}...\n"
            else:  # Linux/Mac
                subprocess.Popen([app_name])  # Works for many applications in PATH
                return f"Opening {app_name}...\n"
        except Exception as e:
            return f"Error: Could not open {app_name}. {e}\n"

    def clear_terminal(self):
        # Clears the content of the terminal
        self.text_area.delete("1.0", tk.END)  # Delete everything in the text widget
        # Do not insert the prompt here, as it will be handled by on_enter

    def on_backspace(self, event):
        # Get the cursor's position to ensure we only remove the last character of the current command
        cursor_position = self.text_area.index(tk.INSERT)
        line_start = f"{cursor_position.split('.')[0]}.0"
        line_end = f"{cursor_position.split('.')[0]}.end"
        
        # Get the current line text
        current_line = self.text_area.get(line_start, line_end).strip()

        # If the current line is empty (no text to delete), prevent the backspace from deleting the prompt
        if current_line == "":
            return "break"  # Prevent deletion when the prompt is empty

        # Allow the backspace to delete only the current line's text
        self.text_area.delete(f"{cursor_position} -1c", cursor_position)
        return "break"  # Prevent the default backspace behavior

    def shutdown_system(self, command):
        try:
            if len(command.split()) == 1:
                # Execute shutdown command (on Linux)
                subprocess.run(["sudo", "shutdown", "now"])
                return "Shutting down system...\n"
            else:
                return "Invalid shutdown command.\n"
        except Exception as e:
            return f"Error: {e}\n"

    def reboot_system(self):
        try:
            subprocess.run(["sudo", "reboot"])
            return "Rebooting system...\n"
        except Exception as e:
            return f"Error: {e}\n"

    def sleep_system(self, command):
        try:
            # Get the sleep duration from the command (e.g., sleep 5)
            duration = int(command.split()[1])
            time.sleep(duration)
            return f"System paused for {duration} seconds.\n"
        except ValueError:
            return "Invalid time duration for sleep.\n"

    def show_calendar(self):
        try:
            result = subprocess.run("cal", shell=True, text=True, capture_output=True)
            return result.stdout if result.stdout else "Error displaying calendar.\n"
        except Exception as e:
            return f"Error: {e}\n"

    def open_calculator(self):
        try:
            subprocess.Popen(["gnome-calculator"])
            return "Opening calculator...\n"
        except Exception as e:
            return f"Error: {e}\n"

    def open_notepad(self):
        try:
            # Opens Notepad on Windows, gedit on Linux
            if os.name == 'nt':  # Windows
                subprocess.Popen(["notepad.exe"])
            else:  # Linux
                subprocess.Popen(["gedit"])
            return "Opening notepad...\n"
        except Exception as e:
            return f"Error: {e}\n"

# Create the Tkinter window
root = tk.Tk()
terminal = TerminalApp(root)
terminal.run()
