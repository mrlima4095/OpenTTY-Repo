#!/usr/bin/python3
# -*- coding: utf-8 -*-
#    
#    python server.py 
#    
#  Copyright (C) 2024 "Mr. Lima"
#  

import socket
import subprocess
import threading
import urllib.request

# Server settings
HOST = '0.0.0.0'  # Listen at current machine
PORT = 4095       # Connection port setting

def handle_client(client_socket, addr):
    print(f"[+] {addr[0]} connected")

    try:
        while True:
            # Receive the command from the client
            command = client_socket.recv(1024).decode('utf-8')

            if not command:
                print(f"[-] {addr[0]} disconnected")
                break
            
            print(f"[+] {addr[0]} -> {command.strip()}")

            command = command.strip().split()
            if command[0] == "get":
                try:
                    if not ' '.join(command[1:]):
                        data = "Missing filename"
                    else:
                        data = open(' '.join(command[1:]), "rt").read()
                except Exception as e:
                    data = e

            elif command[0] == "http":
                if not ' '.join(command[1:]):
                    data = "Missing website URL"
                else:
                    url = ' '.join(command[1:])
                    try:
                        # Using urllib to fetch the content of the URL
                        with urllib.request.urlopen(url) as response:
                            data = response.read().decode('utf-8')
                    except Exception as e:
                        data = e
            
            else:
                data = execute_command(' '.join(command[0:]))
                        
            client_socket.sendall(data.encode('utf-8'))

    except Exception as e:
        print(f"[-] Error with {addr[0]}: {e}")

    finally:
        client_socket.close()

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e.output.decode('utf-8'))

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"OpenTTY Server")
        print(f"")
        print(f"[+] listening at port {PORT}")

        while True:
            client_socket, addr = server_socket.accept()

            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
            
if __name__ == '__main__':
    start_server()