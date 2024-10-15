#!/usr/bin/python3
# -*- coding: utf-8 -*-
#    
#    python server.py 
#    
#  Copyright (C) 2024 "Mr. Lima"
#  

import sys
import socket
import subprocess
import threading
import urllib.request
import os

__version__ = "1.0"

class Server:
    def __init__(self, host='0.0.0.0', port=31522, blacklist_file=None):
        self.host = host
        self.port = port
        self.blacklist_file = blacklist_file

    def blacklist(self, file):
        """Load the list of blocked IPs from a file."""
        if file and os.path.isfile(file):
            with open(file, "rt") as f:
                return set(f.read().splitlines())
        return set()

    def start(self):
        """Start the server and begin listening for connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(50)
            print(f"OpenTTY Server " + __version__)
            print(f"Copyright (C) 2024 - Mr. Lima")
            print(f"")
            print(f"Listening on port {self.port}")

            while True:
                client_socket, addr = server_socket.accept()
                if addr[0] in self.blacklist(self.blacklist_file):
                    print(f"[-] {addr[0]} is blocked")
                    client_socket.sendall("You are on the server blacklist!".encode('utf-8'))
                    client_socket.close()
                else:
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    client_thread.start()

    def handle_client(self, client_socket, addr):
        """Handle a specific client connection and commands."""
        print(f"[+] {addr[0]} connected")

        try:
            while True:
                command = client_socket.recv(1024).decode('utf-8').strip()
                if not command:
                    print(f"[-] {addr[0]} disconnected")
                    break

                print(f"[+] {addr[0]} -> {command}")
                response = self.parse_command(command)
                client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"[-] {addr[0]} -- {e}")

        finally:
            client_socket.close()

    def parse_command(self, command):
        """Parse and execute the command sent by the client."""
        cmd = command.split()[0]

        if cmd == "get": return self.get_file_content(' '.join(command.split()[1:]))
        elif cmd == "http": return self.fetch_url(' '.join(command.split()[1:]))
        else: return self.execute_command(command)

    def get_file_content(self, filename):
        """Read the content of a text file."""
        if not filename:
            return "Filename is missing."
        elif not os.path.isfile(filename):
            return f"File '{filename}' not found."
        else:
            try:
                with open(filename, "rt") as f:
                    return f.read()
            except Exception as e:
                return f"Error opening file: {e}"

    def fetch_url(self, url):
        """Fetch the content of a URL using urllib."""
        if not url:
            return "URL is missing."
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return f"Error accessing URL: {e}"

    def execute_command(self, command):
        """Execute a shell command safely."""
        try: return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as e: return e.output.decode('utf-8')

if __name__ == '__main__':
    if "-u" in sys.argv:
        try:
            with urllib.request.urlopen("https://raw.githubusercontent.com/mrlima4095/OpenTTY-Repo/main/version.txt") as response:
                github_version = response.read().decode('utf-8')

                if github_version != __version__: 
                    print("OpenTTY Server has a new version released!\n\n")
                    print(f"Installed Version - {__version__}")
                    print(f"Avaliable Version - {github_version}")
                else:
                    print("OpenTTY Server is updated")
        except Exception as e: return f"Error accessing URL: {e}"



    else:
        blacklist_file = sys.argv[1] if len(sys.argv) > 1 else None
        server = Server(blacklist_file=blacklist_file)
        server.start()
