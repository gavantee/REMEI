from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import time
import random
import string
import os
import subprocess

hostName = "localhost"
serverPort = 8080

GCC = 'riscv64-elf-gcc'
GDB = 'riscv64-elf-gdb'
QEMU = 'qemu-riscv64'

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
        if (type(path) is str or type(path) is unicode) and path.startswith('/assemble'):
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length)
            print(post_data)
            filename = '/tmp/' + ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
            print(filename)
            f = open(filename + '.c', "a")
            f.write(post_data.decode('utf-8'))
            f.close()
            os.system(GCC + ' -S ' + filename + '.c -o ' + filename + '.s')
            os.system(GCC + ' ' + filename + '.c -o ' + filename + '.o 2> ' + filename + '.stderr')
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            f = open(filename + '.stderr', "r")
            self.wfile.write(bytes(f.read(), 'utf-8'))
            f = open(filename + '.s', "r")
            self.wfile.write(bytes(f.read(), 'utf-8'))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
