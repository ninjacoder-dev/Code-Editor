import tkinter as tk
import re

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.configure_tags()

    def configure_tags(self):
        self.text_widget.tag_configure("Keyword", foreground="#569CD6", font=("Consolas", 10, "bold"))
        self.text_widget.tag_configure("String", foreground="#CE9178")
        self.text_widget.tag_configure("Comment", foreground="#6A9955", font=("Consolas", 10, "italic"))
        self.text_widget.tag_configure("Function", foreground="#DCDCAA")
        self.text_widget.tag_configure("Class", foreground="#4EC9B0")
        self.text_widget.tag_configure("Number", foreground="#B5CEA8")
        self.text_widget.tag_configure("Decorator", foreground="#DCDCAA")

    def highlight(self, event=None):
        content = self.text_widget.get("1.0", tk.END)
        self.text_widget.mark_set("range_start", "1.0")

        for tag in self.text_widget.tag_names():
            self.text_widget.tag_remove(tag, "1.0", tk.END)

        if not hasattr(self, 'current_patterns'):
             self.set_language('python') # Default

        for tag, pattern in self.current_patterns.items():
            self.apply_regex_highlight(tag, pattern, content)

    def set_language(self, language_mode):
        # Common patterns
        number_pattern = r"\b\d+\b"
        string_pattern = r"(\".*?\"|\'.*?\')"
        comment_hash = r"#.*"
        comment_slash = r"//.*|/\*[\s\S]*?\*/"
        
        c_keywords = r"\b(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while|include|define)\b"
        cpp_keywords = c_keywords[:-1] + r"|class|namespace|new|delete|public|private|protected|virtual|friend|this|template|using|try|catch|throw|bool|true|false)\b"
        java_keywords = r"\b(abstract|continue|for|new|switch|assert|default|if|package|synchronized|boolean|do|goto|private|this|break|double|implements|protected|throw|byte|else|import|public|throws|case|enum|instanceof|return|transient|catch|extends|int|short|try|char|final|interface|static|void|class|finally|long|strictfp|volatile|const|float|native|super|while|true|false|null)\b"
        cs_keywords = r"\b(abstract|as|base|bool|break|byte|case|catch|char|checked|class|const|continue|decimal|default|delegate|do|double|else|enum|event|explicit|extern|false|finally|fixed|float|for|foreach|goto|if|implicit|in|int|interface|internal|is|lock|long|namespace|new|null|object|operator|out|override|params|private|protected|public|readonly|ref|return|sbyte|sealed|short|sizeof|stackalloc|static|string|struct|switch|this|throw|true|try|typeof|uint|ulong|unchecked|unsafe|ushort|using|virtual|void|volatile|while)\b"
        php_keywords = r"\b(echo|print|if|else|elseif|while|for|foreach|function|return|class|public|private|protected|static|new|try|catch|throw|namespace|use|include|require)\b"
        html_tags = r"(</?\w+(\s+\w+=\"[^\"]*\")*(\s|/)>)"
        
        patterns_map = {
            "python": {
                "Keyword": r"\b(def|class|if|else|elif|while|for|return|import|from|as|try|except|finally|with|pass|break|continue|lambda|yield|global|nonlocal|raise|del|assert|in|is|not|and|or|True|False|None)\b",
                "String": string_pattern,
                "Comment": comment_hash,
                "Function": r"\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()",
                "Class": r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                "Number": number_pattern,
                "Decorator": r"@[a-zA-Z_][a-zA-Z0-9_]*"
            },
            "c": {
                 "Keyword": c_keywords,
                 "String": string_pattern,
                 "Comment": comment_slash,
                 "Number": number_pattern,
                 "Function": r"\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()"
            },
           "cpp": {
                 "Keyword": cpp_keywords,
                 "String": string_pattern,
                 "Comment": comment_slash,
                 "Number": number_pattern,
                 "Function": r"\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()"
            },
            "java": {
                 "Keyword": java_keywords,
                 "String": string_pattern,
                 "Comment": comment_slash,
                 "Number": number_pattern,
                 "Class": r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                 "Function": r"\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()"
            },
            "csharp": {
                 "Keyword": cs_keywords,
                 "String": string_pattern,
                 "Comment": comment_slash,
                 "Number": number_pattern,
                 "Class": r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                 "Function": r"\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()"
            },
             "php": {
                 "Keyword": php_keywords,
                 "String": string_pattern,
                 "Comment": comment_slash + r"|" + comment_hash,
                 "Number": number_pattern,
                 "Variable": r"\$[a-zA-Z_][a-zA-Z0-9_]*"
            },
            "html": {
                "Tag": r"(</?\w+)",
                "Attribute": r"\s(\w+)=\"",
                "String": r"\"[^\"]*\"",
                "Comment": r"<!--[\s\S]*?-->"
            }
        }
        
        self.current_patterns = patterns_map.get(language_mode, patterns_map["python"])
        
        # Configure extra tags for new languages
        self.text_widget.tag_configure("Tag", foreground="#569CD6")
        self.text_widget.tag_configure("Attribute", foreground="#9CDCFE")
        self.text_widget.tag_configure("Variable", foreground="#9CDCFE") # PHP vars

    def apply_regex_highlight(self, tag, pattern, content):
        for match in re.finditer(pattern, content, re.MULTILINE):
            start = match.start()
            end = match.end()
            start_index = self.text_widget.index(f"1.0 + {start} chars")
            end_index = self.text_widget.index(f"1.0 + {end} chars")
            self.text_widget.tag_add(tag, start_index, end_index)
