import http.server
import socketserver
import webbrowser
import os
import threading
import time
import sys

def find_free_port():
    with socketserver.TCPServer(("localhost", 0), None) as s:
        return s.server_address[1]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    # Override log_message to prevent writing to stderr
    # This prevents the server from crashing when running as a --noconsole executable
    def log_message(self, format, *args):
        pass

def start_server(port):
    # Change directory to the location of the executable or script
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    # If standard outputs are closed (as in noconsole), point them to devnull
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')

    port = find_free_port()
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(1)
    
    # Open the browser
    url = f"http://localhost:{port}/terminal.html"
    webbrowser.open(url)
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)
