import network
import socket
import gc
import ujson
import os

gc.collect()

class UWebServer:
    def __init__(self, port=80, request_size_limit=1024, static_dir=None):
        self.routes = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', port))
        self.s.listen(5)
        self.static_dir = static_dir
        self.request_size_limit = request_size_limit

    def route(self, path, method):
        def decorator(f):
            self.routes[(path, method)] = f
            return f
        return decorator

    def start(self):
        while True:
            try:
                if gc.mem_free() < 102000:
                    gc.collect()

                conn, addr = self.s.accept()
                print('[INFO] Got a connection from %s' % str(addr))

                conn.settimeout(3.0)
                request = conn.recv(self.request_size_limit)
                conn.settimeout(None)
                request = str(request, 'utf-8')

                response_body, content_type, response_code = self.handle_request(request)
                response_body = str(response_body)

                conn.sendall(f'HTTP/1.1 {response_code}\r\n'.encode('utf-8'))
                conn.sendall(f'Content-Type: {content_type}\r\n'.encode('utf-8'))
                conn.sendall('Connection: close\r\n'.encode('utf-8'))
                conn.sendall(f'Content-Length: {len(response_body)}\r\n\r\n'.encode('utf-8'))
                conn.sendall(response_body.encode('utf-8'))
                conn.close()

            except OSError as e:
                print('[ERROR] OSError: %s' % str(e))
                conn.close()

            except Exception as e:
                print('[ERROR] Exception: %s' % str(e))
                conn.close()

    def parse_request(self, request):
        headers_section, body = request.split('\r\n\r\n', 1)  # Split request into headers and body
        request_lines = headers_section.split('\r\n')  # Split headers into lines

        headers = {}
        method, path, version = request_lines[0].split()
        for line in request_lines[1:]:
            k, v = line.split(':', 1)
            headers[k.strip()] = v.strip()

        return method, path, version, headers, body


    def handle_request(self, request):
        method, path, version, headers, body = self.parse_request(request)
        
        print('[INFO] %s %s %s' % (str(method), str(path), str(version)))
        
        path = self.sanitize_path(path)

        for (route_path, route_method), handler in self.routes.items():
            try:
                if path == route_path and method == route_method:
                    if method == "POST":
                        response_body, content_type, status_code = handler(body)
                        return response_body, content_type, status_code
                    elif method == "GET" or method == "HEAD":
                        response_body, content_type, status_code = handler()
                        return response_body, content_type, status_code
                    elif method == "OPTIONS":
                        response_body, content_type, status_code = handler()
                        return response_body, content_type, status_code
                    else:
                        return 'Unsupported method', 'text/html', '405 Method Not Allowed'
            except Exception as e:
                print('[ERROR] Exception: %s' % str(e))
                return 'Internal Server Error', 'text/html', '500 Internal Server Error'

        if self.static_dir and method == "GET":
            if path == "/":
                static_file_path = self.static_dir + '/index.html'
            else:
                static_file_path = self.static_dir + '/' + path.lstrip('/')
            try:
                with open(static_file_path, 'r') as f:
                    if f.read():
                        return self.handle_static_file_request(static_file_path)
            except OSError:
                pass

        return "Not Found", "text/html", '404 Not Found'

    def handle_static_file_request(self, file_path):
        ext = file_path.split('.')[-1]
        content_type = {
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript',
            'jpg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'ico': 'image/x-icon'
        }.get(ext, 'application/octet-stream')
        try:
            with open(file_path, 'r') as f:
                response_body = f.read()
            return response_body, content_type, '200 OK'
        except Exception as e:
            return f"File not found: {str(e)}", "text/html", '404 Not Found'
    
    def sanitize_path(self, path):
        parts = path.split('/')
        parts = [p for p in parts if p != '..']
        return '/'.join(parts)
