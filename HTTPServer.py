import socket
import json


class HTTPServer:
    # Routes is an array and an element of its is like {"/": lambda: "Hello World", "method": "GET"}.
    routes = []

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen(self, port: int):
        self.server_socket.bind(("127.0.0.1", port))
        self.server_socket.listen(10)

        active_routes = [list(route.keys())[0] for route in self.routes]

        # Todo: Add threading.
        while True:
            client_socket, _ = self.server_socket.accept()
            req = client_socket.recv(1024)

            req = HTTPRequest(req)
            res = HTTPResponse()

            if req.path not in active_routes:
                res.status = 404
                res.send("404 page not found.")
                client_socket.send(res.__bytes__())
                client_socket.close()
                continue

            for route in self.routes:
                path = list(route.keys())[0]
                callback = route[path]

                method = route["method"]

                if req.path == path and req.method == method:
                    callback(req, res)
                    break
                elif req.path == path and req.method != method:
                    res.status = 405
                    res.send(f"Can't {req.method} {path}")

            client_socket.send(res.__bytes__())
            client_socket.close()

    def get(self, path: str, callback):
        self.routes.append({path: callback, "method": "GET"})

    def post(self, path: str, callback):
        self.routes.append({path: callback, "method": "POST"})


class HTTPRequest:
    def __init__(self, req: bytes):
        req_arr = req.decode("utf-8").split("\n\r")
        req_lines = req_arr[0].splitlines()

        req_line = req_lines[0]

        self.method = req_line.split(" ")[0]
        self.path = req_line.split(" ")[1]

        self.headers = {}
        for line in req_lines[1:]:
            if line:
                key, value = line.split(": ")
                self.headers[key] = value

        if self.method == "POST":
            self.body = req_arr[-1]
        else:
            self.body = None


class HTTPResponse:
    def __init__(self):
        self.status = 200
        self.headers = {}
        self.body = ""

    def __bytes__(self):
        header = f"HTTP/1.1 {self.status}\n"
        for key, value in self.headers.items():
            header += f"{key}: {value}\n"

        header += "\n"

        return (header + self.body).encode("utf-8")
    
    def text(self, body: str, status: int = 200):
        self.body = body
        self.status = status

        self.headers["Content-Type"] = "text/plain"
        self.headers["Content-Length"] = len(self.body)

    def send(self, body: str, status: int = 200):
        self.body = body
        self.status = status

        self.headers["Content-Type"] = "text/html"
        self.headers["Content-Length"] = len(self.body)
    
    def json(self, body_dict: dict, status: int = 200):
        self.body = json.dumps(body_dict)
        self.status = status

        self.headers["Content-Type"] = "application/json"
        self.headers["Content-Length"] = len(self.body)

    def send_file(self, file_path: str):
        # Not effective.
        with open(file_path, "r") as f:
            self.body = f.read()

        self.headers["Content-Type"] = "text/html"
        self.headers["Content-Length"] = len(self.body)