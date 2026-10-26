import socket

HOST = "localhost"
PORT = 8000
PATH = "/index.html"

request = f"GET {PATH} HTTP/1.1\r\nHost: {HOST}\r\nConnection: close\r\n\r\n"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(request.encode())

    svar = b""
    while True:
        data = s.recv(4096)
        if not data:
            break
        svar += data

print(svar.decode())
