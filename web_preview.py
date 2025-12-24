import http.server
import socketserver
import threading
import webbrowser
import os
import subprocess
import random

class WebPreview:
    def __init__(self, output_callback):
        self.server = None
        self.port = 8000
        self.thread = None
        self.output_callback = output_callback

    def preview_file(self, filepath):
        """
        Launches a local server (or php server) and opens the browser.
        """
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()

        # Find a free port
        self.port = random.randint(8000, 9000)

        if ext == ".php":
            self.run_php_server(directory, filename)
        else:
            self.run_static_server(directory, filename)

    def run_php_server(self, directory, filename):
        # PHP built-in server
        cmd = ["php", "-S", f"localhost:{self.port}", "-t", directory]
        self.output_callback(f"Starting PHP server at http://localhost:{self.port}...\n", "stdout")
        
        def run_server():
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        threading.Thread(target=run_server, daemon=True).start()
        webbrowser.open(f"http://localhost:{self.port}/{filename}")

    def run_static_server(self, directory, filename):
        os.chdir(directory)
        handler = http.server.SimpleHTTPRequestHandler
        
        # Stop previous server if running (simple implementation: just use new port)
        # Ideally we'd manage the server lifecycle better, but for MVP:
        
        try:
            self.server = socketserver.TCPServer(("localhost", self.port), handler)
        except OSError:
            # Port busy, try another
            self.port += 1
            self.server = socketserver.TCPServer(("localhost", self.port), handler)

        self.output_callback(f"Starting Web server at http://localhost:{self.port}...\n", "stdout")
        
        def serve():
            self.server.serve_forever()
            
        threading.Thread(target=serve, daemon=True).start()
        webbrowser.open(f"http://localhost:{self.port}/{filename}")
