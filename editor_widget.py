import tkinter as tk
from tkinter import ttk
from syntax_highlighter import SyntaxHighlighter

class EditorWidget(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()
        self.setup_layout()
        self.bind_events()
        self.highlighter = SyntaxHighlighter(self.text_area)

    def create_widgets(self):
        self.text_area = tk.Text(self, wrap=tk.NONE, undo=True, font=("Consolas", 10), bg="#1E1E1E", fg="#D4D4D4", insertbackground="white")
        self.line_numbers = tk.Text(self, width=4, padx=3, takefocus=0, border=0, background="#2D2D30", foreground="#858585", state="disabled", font=("Consolas", 10))
        self.scrollbar_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.on_scroll)
        self.scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text_area.xview)
        
        self.text_area.configure(yscrollcommand=self.sync_scroll, xscrollcommand=self.scrollbar_x.set)

    def setup_layout(self):
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def bind_events(self):
        self.text_area.bind("<KeyRelease>", self.on_content_changed)
        self.text_area.bind("<Button-1>", self.on_cursor_move)
        self.text_area.bind("<<Change>>", self.on_content_changed)
        self.text_area.bind("<Return>", self.auto_indent)

    def on_scroll(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def sync_scroll(self, *args):
        self.scrollbar_y.set(*args)
        self.line_numbers.yview_moveto(args[0])

    def on_content_changed(self, event=None):
        self.update_line_numbers()
        self.highlighter.highlight()

    def on_cursor_move(self, event=None):
        pass # Can be used for status bar updates

    def update_line_numbers(self):
        line_count = int(self.text_area.index("end-1c").split(".")[0])
        line_numbers_content = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_content)
        self.line_numbers.config(state="disabled")

    def auto_indent(self, event):
        # Basic auto-indentation
        line_index = self.text_area.index("insert").split(".")[0]
        line_text = self.text_area.get(f"{line_index}.0", f"{line_index}.end")
        indentation = ""
        for char in line_text:
            if char == " ":
                indentation += " "
            elif char == "\t":
                indentation += "\t"
            else:
                break
        
        # Add extra indent if line ends with :
        if line_text.strip().endswith(":"):
            indentation += "    "
        
        self.text_area.insert("insert", "\n" + indentation)
        return "break" # Prevent default return behavior

    def get_text(self):
        return self.text_area.get("1.0", tk.END)

    def set_text(self, text):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
        self.on_content_changed()
