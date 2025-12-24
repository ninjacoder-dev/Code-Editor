import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import webbrowser

# Add current directory to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from editor_widget import EditorWidget
from execution_manager import ExecutionManager
from linter_integration import LinterIntegration
from web_preview import WebPreview
from config_manager import ConfigManager

class PythonEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Editor")
        self.root.geometry("1000x800")
        
        self.config_manager = ConfigManager()
        self.tabs = {} # Map tab_id -> {"editor": widget, "path": filepath}
        self.execution_manager = ExecutionManager(self.append_output, self.config_manager, self.handle_missing_dependency)
        self.web_preview = WebPreview(self.append_output)
        self.linter = LinterIntegration()
        
        self.create_menu()
        self.create_toolbar()
        self.create_panes()
        self.bind_shortcuts()
        
        # Start with one empty tab
        self.new_file()

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#333333")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        btn_style = {"bg": "#3C3C3C", "fg": "white", "relief": tk.FLAT, "padx": 10, "pady": 2, "activebackground": "#505050", "activeforeground": "white"}
        
        tk.Button(toolbar, text="Run Python", command=lambda: self.run_specific("python"), **btn_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Run C", command=lambda: self.run_specific("c"), **btn_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Run C++", command=lambda: self.run_specific("cpp"), **btn_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Run Java", command=lambda: self.run_specific("java"), **btn_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Run C#", command=lambda: self.run_specific("csharp"), **btn_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Preview Web", command=lambda: self.run_specific("web"), **btn_style).pack(side=tk.LEFT, padx=2, pady=2)
        
        tk.Label(toolbar, text="|", bg="#333333", fg="#555555").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="Close Tab", command=self.close_current_tab, **btn_style).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Clear Output", command=self.clear_output, **btn_style).pack(side=tk.LEFT, padx=2, pady=2)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", command=self.close_current_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Run Menu
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run Code", accelerator="F5", command=self.run_code)
        run_menu.add_command(label="Check Syntax", command=self.check_syntax)
        menubar.add_cascade(label="Run", menu=run_menu)
        
        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Configure Compilers", command=self.open_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        self.root.config(menu=menubar)

    def create_panes(self):
        # PanedWindow for split (Editor Top, Output Bottom)
        self.paned_window = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=5, bg="#333333")
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Editor Section
        # Editor Section using Notebook for Tabs
        self.notebook = ttk.Notebook(self.paned_window)
        self.paned_window.add(self.notebook, height=500)
        
        # Close on middle click
        self.notebook.bind("<Button-2>", self.on_tab_middle_click)
        
        # Output Section
        self.output_frame = tk.Frame(self.paned_window, bg="#1E1E1E")
        self.paned_window.add(self.output_frame)
        
        self.output_label = tk.Label(self.output_frame, text="Terminal / Output", bg="#252526", fg="#CCCCCC", anchor="w")
        self.output_label.pack(fill=tk.X)
        
        self.output_text = tk.Text(self.output_frame, height=10, bg="#1E1E1E", fg="#CCCCCC", font=("Consolas", 10), state="disabled")
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-S>", lambda event: self.save_as_file())
        self.root.bind("<F5>", lambda event: self.run_code())

    def get_current_tab_id(self):
        return self.notebook.select()

    def get_active_editor(self):
        tab_id = self.get_current_tab_id()
        if tab_id:
            return self.tabs[tab_id]["editor"]
        return None

    def get_active_path(self):
        tab_id = self.get_current_tab_id()
        if tab_id:
            return self.tabs[tab_id]["path"]
        return None
    
    def set_active_path(self, path):
         tab_id = self.get_current_tab_id()
         if tab_id:
             self.tabs[tab_id]["path"] = path
             self.notebook.tab(tab_id, text=os.path.basename(path) if path else "Untitled")
             self.root.title(f"Code Editor - {path}")

    def new_file(self):
        new_editor = EditorWidget(self.notebook)
        self.notebook.add(new_editor, text="Untitled")
        self.notebook.select(new_editor)
        
        # Store ref
        # In Tkinter, the tab identifier is the widget name/id usually, or we can use the widget object itself key if we manage carefully.
        # notebook.select() returns the window name (str).
        tab_id = self.notebook.select()
        self.tabs[tab_id] = {"editor": new_editor, "path": None}
        new_editor.highlighter.set_language("python") # Default

    def close_current_tab(self):
        tab_id = self.get_current_tab_id()
        if tab_id:
            self.notebook.forget(tab_id)
            del self.tabs[tab_id]

    def on_tab_middle_click(self, event):
        try:
            tab_id = self.notebook.identify(event.x, event.y)
            if tab_id:
                # "identify" might return an element name like "label", we need the tab index
                index = self.notebook.index(f"@{event.x},{event.y}")
                tab_widget_name = self.notebook.tabs()[index]
                self.notebook.forget(index)
                
                # We need to find the key in self.tabs where editor widget matches tab_widget_name
                # This is tricky because self.tabs uses select() id.
                # Actually, tab_widget_name IS the key returned by select().
                if tab_widget_name in self.tabs:
                    del self.tabs[tab_widget_name]
        except Exception:
            pass

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".py", filetypes=[("All Files", "*.*")])
        if file_path:
            try:
                # Create new tab for opened file
                self.new_file()
                editor = self.get_active_editor()
                
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                editor.set_text(content)
                self.set_active_path(file_path)
                
                self.clear_output()
                self.append_output(f"Loaded {file_path}\n", "stdout")
                
                # Detect Language
                ext = os.path.splitext(file_path)[1].lower()
                lang_map = {
                    ".py": "python", ".c": "c", ".cpp": "cpp", ".cc": "cpp",
                    ".java": "java", ".cs": "csharp", ".php": "php",
                    ".html": "html", ".htm": "html"
                }
                editor.highlighter.set_language(lang_map.get(ext, "python"))
                editor.highlighter.highlight()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        current_path = self.get_active_path()
        if current_path:
             try:
                editor = self.get_active_editor()
                content = editor.get_text()
                with open(current_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.append_output(f"Saved {current_path}\n", "stdout")
             except Exception as e:
                 messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            self.set_active_path(file_path)
            self.save_file()

    def run_code(self):
        editor = self.get_active_editor()
        if not editor: return

        # Auto-save before running if possible, or save to temp
        content = editor.get_text()
        
        if not content.strip():
            return

        run_path = self.get_active_path()
        if not run_path:
             # Force save as for unsaved files in multi-tab
             if not self.save_as_file():
                  return
             run_path = self.get_active_path()
        else:
            # Save current state
            self.save_file()

        # Check if it is a web file
        ext = os.path.splitext(run_path)[1].lower()
        if ext in [".html", ".htm", ".php"]:
             self.web_preview.preview_file(run_path)
             return

        self.clear_output()
        self.append_output(f"Running {run_path}...\n", "stdout")
        self.execution_manager.run_file(run_path)

    def run_specific(self, lang):
        current_path = self.get_active_path()
        if not current_path:
            messagebox.showwarning("Warning", "Please save the file first.")
            return

        ext = os.path.splitext(current_path)[1].lower()
        map_ext = {
            "python": [".py"],
            "c": [".c"],
            "cpp": [".cpp", ".cc"],
            "java": [".java"],
            "csharp": [".cs"],
            "web": [".html", ".htm", ".php"]
        }
        
        valid_exts = map_ext.get(lang, [])
        if ext not in valid_exts:
             messagebox.showwarning("Mismatch", f"Current file ({ext}) does not match the selected language runner ({lang}).")
             return
             
        # Reuse generic run logic which dispatches based on extension
        self.run_code()

    def check_syntax(self):
        editor = self.get_active_editor()
        if not editor: return
        content = editor.get_text()
        error = self.linter.check_syntax(content)
        self.clear_output()
        if error:
            self.append_output(f"LINT ERROR: {error}\n", "stderr")
        else:
            self.append_output("No syntax errors found.\n", "stdout")

    def append_output(self, text, stream_name):
        self.output_text.config(state="normal")
        tag = "error" if stream_name == "stderr" else "output"
        
        # Configure tags if not already
        self.output_text.tag_config("error", foreground="#F48771")
        self.output_text.tag_config("output", foreground="#CCCCCC")
        
        self.output_text.insert(tk.END, text, tag)
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")

    def clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state="disabled")

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Configure Compilers")
        settings_win.geometry("400x300")
        
        tk.Label(settings_win, text="Compiler / Runtime Paths", font=("Arial", 10, "bold")).pack(pady=10)
        
        fields = {
            "C Compiler (gcc)": "c_compiler",
            "C++ Compiler (g++)": "cpp_compiler",
            "Java Compiler (javac)": "java_compiler",
            "Java Runtime (java)": "java_runtime",
            "C# Compiler (csc)": "csharp_compiler",
            "PHP Runtime (php)": "php_runtime"
        }
        
        entries = {}
        
        frame = tk.Frame(settings_win)
        frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        row = 0
        for label, key in fields.items():
            tk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
            entry = tk.Entry(frame, width=30)
            entry.insert(0, self.config_manager.get(key))
            entry.grid(row=row, column=1, sticky="ew", pady=2)
            entries[key] = entry
            row += 1
            
        def save_settings():
            for key, entry in entries.items():
                self.config_manager.set(key, entry.get())
            messagebox.showinfo("Saved", "Settings saved successfully.")
            settings_win.destroy()
            
        tk.Button(settings_win, text="Save", command=save_settings, bg="#3C3C3C", fg="white").pack(pady=10)

    def handle_missing_dependency(self, tool):
        # normalize tool name (remove extension, path)
        base_tool = os.path.basename(tool).lower().replace(".exe", "")
        
        DOWNLOAD_URLS = {
            "gcc": "https://www.mingw-w64.org/downloads/",
            "g++": "https://www.mingw-w64.org/downloads/",
            "javac": "https://adoptium.net/",
            "java": "https://adoptium.net/",
            "csc": "https://dotnet.microsoft.com/download/dotnet-framework",
            "python": "https://www.python.org/downloads/",
            "php": "https://www.php.net/downloads"
        }
        
        # Fuzzy match or direct match
        url = DOWNLOAD_URLS.get(base_tool)
        
        if url:
             if messagebox.askyesno("Missing Dependency", f"The required tool '{base_tool}' was not found.\nDo you want to open the download page?"):
                 webbrowser.open(url)
        else:
            messagebox.showerror("Missing Dependency", f"The required tool '{tool}' was not found.\nPlease install it and check your settings.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PythonEditorApp(root)
    root.mainloop()

