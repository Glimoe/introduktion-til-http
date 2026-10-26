import socket

HOST = "127.0.0.1"
PORT = 8000

body = "<!doctype html><html><body><h1>Hej fra min egen server</h1></body></html>"

svar = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html\r\n"
    f"Content-Length: {len(body.encode())}\r\n"
    "\r\n"
    + body
)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Lytter på {HOST}:{PORT} ...")

    while True:
        conn, addr = s.accept()
        with conn:
            request = conn.recv(4096)
            print("Request modtaget fra", addr)
            print(request.decode())
            conn.sendall(svar.encode())
