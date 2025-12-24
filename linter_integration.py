import ast

class LinterIntegration:
    def __init__(self):
        pass

    def check_syntax(self, code):
        """
        Checks for syntax errors using the ast module.
        Returns a string describing the error or None if no error.
        """
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            return f"Syntax Error on line {e.lineno}, col {e.offset}: {e.msg}"
        except Exception as e:
            return f"Error checking code: {e}"
