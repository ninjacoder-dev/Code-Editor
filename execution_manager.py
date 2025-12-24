import subprocess
import threading
import sys
import os
import shutil

class ExecutionManager:
    def __init__(self, output_callback, config_manager=None, missing_dep_callback=None):
        self.output_callback = output_callback
        self.missing_dep_callback = missing_dep_callback
        self.process = None
        self.config_manager = config_manager

    def run_code(self, code, cwd=None):
        # Create a temporary file to run the code
        # Ideally we should run the saved file, but for unsaved buffers we can use a temp file
        # For this MVP, we will assume we are passed the code content and valid cwd or just run as is.
        # However, running from a string is cleaner via -c but tricky with newlines.
        # Best approach: WRITE to a temp file or the current file if it exists.
        
        # We'll rely on the caller to provide a filepath if saved, or write to a temp file.
        # For simplicity here: The main app will save to a temp file if not saved.
        pass # Only useful if we have the file path.

    def run_file(self, filepath):
        if self.process and self.process.poll() is None:
            self.stop_execution()
        
        # 1. Get the command tuple AND the required tool name
        command_data, is_web = self.get_execution_command(filepath)
        
        if not command_data and not is_web:
            self.output_callback(f"No execution handler for {os.path.basename(filepath)}\n", "stderr")
            return
            
        if is_web:
            # Handle in main or web preview, but ideally we return here.
            # For now, let's assume this returns a list of args for Popen
            pass 

        # 2. Check dependencies (if not web)
        if command_data and not is_web:
             tool_path = None
             if isinstance(command_data, list):
                 tool_path = command_data[0]
             else:
                 # Shell command string, extract first token (quoted or not)
                 # naive parse: first word or first quoted string
                 import shlex
                 try:
                    tool_path = shlex.split(command_data)[0]
                 except:
                    tool_path = command_data.split()[0]
             
             if tool_path and not os.path.exists(tool_path) and not shutil.which(tool_path):
                 if self.missing_dep_callback:
                     self.missing_dep_callback(tool_path)
                 else:
                     self.output_callback(f"Error: Required tool '{tool_path}' not found.\n", "stderr")
                 return

        try:
             # If it's a list (subprocess args)
            if isinstance(command_data, list):
                 self.start_process(command_data, os.path.dirname(filepath))
            else:
                # If it's a shell string (for compilation && run)
                self.output_callback(f"Executing: {command_data}\n", "stdout")
                self.start_process(command_data, os.path.dirname(filepath), shell=True)
            
        except Exception as e:
            self.output_callback(f"Error starting process: {e}\n", "stderr")

    def get_execution_command(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        basename = os.path.splitext(os.path.basename(filepath))[0]
        
        # Get paths from config or default
        cc = self.config_manager.get("c_compiler") if self.config_manager else "gcc"
        cpp = self.config_manager.get("cpp_compiler") if self.config_manager else "g++"
        javac = self.config_manager.get("java_compiler") if self.config_manager else "javac"
        java = self.config_manager.get("java_runtime") if self.config_manager else "java"
        csc = self.config_manager.get("csharp_compiler") if self.config_manager else "csc"
        php = self.config_manager.get("php_runtime") if self.config_manager else "php"

        if ext == ".py":
            return [sys.executable, "-u", filepath], False
        elif ext == ".c":
            exe_name = basename + ".exe" if os.name == 'nt' else "./" + basename
            return f'"{cc}" "{filepath}" -o "{basename}" && "{exe_name}"', False
        elif ext == ".cpp" or ext == ".cc":
            exe_name = basename + ".exe" if os.name == 'nt' else "./" + basename
            return f'"{cpp}" "{filepath}" -o "{basename}" && "{exe_name}"', False
        elif ext == ".java":
            return f'"{javac}" "{filepath}" && "{java}" "{basename}"', False
        elif ext == ".cs":
            exe_name = basename + ".exe" if os.name == 'nt' else "./" + basename
            return f'"{csc}" "{filepath}" && "{exe_name}"', False
        elif ext == ".php":
            return [php, filepath], False
        elif ext in [".html", ".htm"]:
             # This should be handled by web preview, but providing a hook
            return None, True
        return None, False

    def start_process(self, command, cwd, shell=False):
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=cwd,
            shell=shell
        )
        threading.Thread(target=self._read_stream, args=(self.process.stdout, "stdout"), daemon=True).start()
        threading.Thread(target=self._read_stream, args=(self.process.stderr, "stderr"), daemon=True).start()

    def _read_stream(self, stream, stream_name):
        try:
            for line in stream:
                self.output_callback(line, stream_name)
        except Exception:
            pass
        finally:
            stream.close()
            # Check if process ended
            if self.process:
                self.process.poll()
                if self.process.returncode is not None:
                    # Could notify exit code if desired
                    pass

    def stop_execution(self):
        if self.process:
            self.process.terminate()
            self.process = None
            self.output_callback("[Process stopped]\n", "stderr")
