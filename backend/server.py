from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import time
import random
import string
import os
import threading
import subprocess
import json
from pygdbmi.gdbcontroller import GdbController

hostName = "localhost"
serverPort = 8080

GCC = 'riscv64-elf-gcc'
GDB = 'riscv64-elf-gdb'
QEMU = 'qemu-riscv64'

gdbmi = {}

def run_qemu(file, port):
    print(["sh", "-c", f"{QEMU} -g {port} {file}.o"])
    subprocess.call(["sh", "-c", f"{QEMU} -g {port} {file}.o"])

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        #if (type(path) is str or type(path) is unicode) and path.startswith('/next'):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>EGT</title></head>", "utf-8"))
    def do_POST(self):
        path = self.path
        if (type(path) is str or type(path) is unicode) and path.startswith('/compile'):
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length)
            print(post_data)
            filename = '/tmp/' + ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
            print(filename)
            f = open(f"{filename}.c", "a")
            f.write(post_data.decode('utf-8'))
            f.close()
            os.system(f'{GCC} -S {filename}.c -o {filename}.s')
            os.system(f'{GCC} -ggdb {filename}.c -o {filename}.o 2> {filename}.stderr')
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            res = {}
            try:
                f = open(f"{filename}.s", "r")
                res["code"] = f.read()
                res["errors"] = ""
            except:
                f = open(f"{filename}.stderr", "r")
                res["code"] = ""
                res["errors"] = f.read()
            
            # Qemu <-> GDB port
            port  = random.randint(10000, 50000)
            res["port"] = port
            self.wfile.write(bytes(json.dumps(res), "utf-8"))
            threading.Thread(target=run_qemu, args = [filename, port]).start()
            gdbmi[port] = GdbController([GDB, "--interpreter=mi3", f"{filename}.o"])
            print(gdbmi[port].write(f"target remote localhost:{port}"))
        elif (type(path) is str or type(path) is unicode) and path.startswith('/command'):
            length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(length))
            port = post_data["port"]
            print(port)
            response = gdbmi[port].write(post_data["command"])
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
