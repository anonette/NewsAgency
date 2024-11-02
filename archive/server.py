import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, unquote
from http import HTTPStatus
import mimetypes

class ArchiveHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for all responses
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)

        # Set content type based on file extension
        ext = os.path.splitext(path)[1]
        if ext == '.mp3':
            content_type = 'audio/mpeg'
        elif ext == '.json':
            content_type = 'application/json'
        else:
            content_type = 'text/plain'

        # Handle requests for directory listings
        if path.startswith('/list/'):
            country_code = path.split('/')[-1]
            archive_path = os.path.join('..', 'text_archive', country_code)
            try:
                files = [f for f in os.listdir(archive_path) if f.endswith('_log.json')]
                files.sort(reverse=True)
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(files).encode())
                return
            except Exception as e:
                print(f"Error listing directory: {str(e)}")
                self.send_error(HTTPStatus.NOT_FOUND, f"Directory not found: {str(e)}")
                return

        # Handle requests for text archive files
        if path.startswith('/text_archive/'):
            try:
                file_path = os.path.join('..', path.lstrip('/'))
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(content.encode())
                return
            except Exception as e:
                print(f"Error reading file: {str(e)}")
                self.send_error(HTTPStatus.NOT_FOUND, f"File not found: {str(e)}")
                return

        # Handle requests for audio files
        if path.startswith('/archive/'):
            try:
                file_path = os.path.join('..', path.lstrip('/'))
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                print(f"Error reading audio file: {str(e)}")
                self.send_error(HTTPStatus.NOT_FOUND, f"Audio file not found: {str(e)}")
                return

        # Handle all other requests
        self.send_error(HTTPStatus.NOT_FOUND, "Resource not found")

def run(server_class=socketserver.TCPServer, handler_class=ArchiveHandler, port=8000):
    # Allow server to be restarted
    server_class.allow_reuse_address = True
    
    # Get port from environment variable if available (for cloud deployment)
    port = int(os.environ.get('PORT', port))
    
    # Bind to all available interfaces
    server_address = ('', port)
    
    with server_class(server_address, handler_class) as httpd:
        print(f"Starting server on port {port}...")
        print(f"Current directory: {os.getcwd()}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

if __name__ == "__main__":
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run()
