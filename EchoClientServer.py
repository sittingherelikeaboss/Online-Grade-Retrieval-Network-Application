#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys

# Lab 2 Libraries
import csv
import getpass
import hashlib

########################################################################
# Echo-Server class
########################################################################

class Server:

    HOSTNAME = socket.gethostname()
    PORT = 50000

    RECV_SIZE = 1024
    BACKLOG = 10
    
    MSG_ENCODING = "utf-8"

    def __init__(self):
        self.mark_database = []
        self.output_csv_file()
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        print("-" * 72)
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Get socket layer socket options.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket.bind( (Server.HOSTNAME, Server.PORT) )

            # Set socket to listen state.
            self.socket.listen(Server.BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                # Block while waiting for incoming connections. When
                # one is accepted, pass the new socket reference to
                # the connection handler.
                self.connection_handler(self.socket.accept())
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))

        while True:

            try:
                
                # Receive bytes over the TCP connection. This will block
                # until "at least 1 byte or more" is available.
                recvd_bytes = connection.recv(Server.RECV_SIZE)
                
                # If recv returns with zero bytes, the other end of the
                # TCP connection has closed (The other end is probably in
                # FIN WAIT 2 and we are in CLOSE WAIT.). If so, close the
                # server end of the connection and get the next client
                # connection.
                if len(recvd_bytes) == 0:
                    print("Closing client connection ... ")
                    connection.close()
                    break
                
                # Decode the received bytes back into strings. Then output
                # them.
                #recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
                
                #print("Received IP/password hash ", recvd_str, " from client")
                print("Received ID/password hash ", recvd_bytes, " from client")
                
                # Send the received bytes back to the client.
                found_student, student_marks = self.find_student(recvd_bytes)
                print("Found student", found_student, "Student_marks", student_marks)
                
                if found_student == True:
                    print("Correct password, record found.")
                else:
                    print("Invalid ID or password.")

                connection.sendall(student_marks.encode(Server.MSG_ENCODING))
                print("Sent: ", student_marks)

            except KeyboardInterrupt:
                print()
                print("Closing client connection ... ")
                connection.close()
                break

    def output_csv_file(self):
        print("Input data read from CSV file:")
        with open('course_grades_v01.csv', newline = '') as csvfile:
            spamreader = csv.reader(csvfile, delimiter = ',', quotechar = '|')
            for row in spamreader:
                print(','.join(row))
                self.mark_database.append(row)

    def find_student(self, hash_info):
        found = False
        marks = "Password failure"
        for row in range(1, len(self.mark_database)):
            HASH_OBJ = hashlib.sha256()
            HASH_OBJ.update((self.mark_database[row][0]).encode(Server.MSG_ENCODING)) # ID number hash
            HASH_OBJ.update((self.mark_database[row][1]).encode(Server.MSG_ENCODING)) # Password hash
            hash_info2 = HASH_OBJ.digest()
            if hash_info == hash_info2:
                marks = (self.mark_database[0][4] + ': ' + self.mark_database[row][4] + ', ') # Midterm
                marks += (self.mark_database[0][5] + ': ' + self.mark_database[row][5] + ', ') # Lab 1
                marks += (self.mark_database[0][6] + ': ' + self.mark_database[row][6] + ', ') # Lab 2
                marks += (self.mark_database[0][7] + ': ' + self.mark_database[row][7] + ', ') # Lab 3
                marks += (self.mark_database[0][8] + ': ' + self.mark_database[row][8]) # Lab 4
                found = True
                break
        return found, marks

    

########################################################################
# Echo-Client class
########################################################################

class Client:

    SERVER_HOSTNAME = socket.gethostname()
    RECV_SIZE = 1024

    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.send_console_input_forever()
        
    def get_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((Client.SERVER_HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input_id(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered.
        while True:
            self.input_id = input('ID Number: ')
            if self.input_id != '':
                print("ID number", self.input_id, "received.")
                break

    def get_console_input_pw(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered.
        while True:
            self.input_pw = getpass.getpass(prompt = 'Password: ', stream = None)
            if self.input_pw != '':
                break            
    
    def send_console_input_forever(self):
        while True:
            try:
                # Lab 2
                self.get_console_input_id() 
                self.get_console_input_pw()
                
                self.connection_send()
                self.connection_receive() 
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                self.socket.close()
                sys.exit(1)

    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
            
            HASH_OBJ = hashlib.sha256()
            HASH_OBJ.update(self.input_id.encode(Server.MSG_ENCODING))
            HASH_OBJ.update(self.input_pw.encode(Server.MSG_ENCODING))
            self.to_send = HASH_OBJ.digest()
            self.socket.sendall(self.to_send)
            print("ID/password hash", self.to_send, "sent to server.")
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            # Receive and print out text. The received bytes objects
            # must be decoded into string objects.
            recvd_bytes = self.socket.recv(Client.RECV_SIZE)

            # recv will block if nothing is available. If we receive
            # zero bytes, the connection has been closed from the
            # other end. In that case, close the connection on this
            # end and exit.
            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            print("Received: ", recvd_bytes.decode(Server.MSG_ENCODING))

        except Exception as msg:
            print(msg)
            sys.exit(1)

########################################################################
# Process command line arguments if run directly.
########################################################################

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role', choices=roles, help='server or client role', required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################





