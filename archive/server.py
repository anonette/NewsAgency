import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, unquote

class ArchiveHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)

        # Serve index.html for root path
        if path == '/':
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        # Handle requests for directory listings
        if path.startswith('/list/'):
            country_code = path.split('/')[-1]
            archive_path = os.path.join('..', 'text_archive', country_code)
            try:
                files = [f for f in os.listdir(archive_path) if f.endswith('_log.json')]
                files.sort(reverse=True)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(files).encode())
                return
            except Exception as e:
                print(f"Error listing directory: {str(e)}")
                self.send_error(404, f"Directory not found: {str(e)}")
                return

        # Handle requests for text archive files
        if path.startswith('/text_archive/'):
            try:
                file_path = os.path.join('..', path.lstrip('/'))
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content.encode())
                return
            except Exception as e:
                print(f"Error reading file: {str(e)}")
                self.send_error(404, f"File not found: {str(e)}")
                return

        # Handle requests for audio files
        if path.startswith('/archive/'):
            try:
                file_path = os.path.join('..', path.lstrip('/'))
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'audio/mpeg')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                print(f"Error reading audio file: {str(e)}")
                self.send_error(404, f"Audio file not found: {str(e)}")
                return

        # Handle all other requests normally
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

if __name__ == "__main__":
    PORT = 8000
    Handler = ArchiveHandler
    
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Current directory: {os.getcwd()}")
        httpd.serve_forever()
