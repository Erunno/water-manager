import http.server
import ssl
import sys

def run_server(port=4443):
    handler = http.server.SimpleHTTPRequestHandler
    
    httpd = http.server.HTTPServer(('0.0.0.0', port), handler)
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='server.cert', keyfile='server.key')
    
    # Apply SSL context to server
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f"Serving HTTPS on 0.0.0.0 port {port} (https://localhost:{port}/) ...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, shutting down server")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4443
    run_server(port)
