import sys
import getopt
import time
import random
import os
import math

import Checksum
import BasicSender

class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False):
        super(Sender, self).__init__(dest, port, filename, debug)

    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print("recv: %s" % response_packet)
        else:
            print("recv: %s <--- CHECKSUM FAILED" % response_packet)

    # Main sending loop.
    def start(self):

        def resend_packet(packet):
            self.send(packet.encode())
            response = self.receive(1)
            return response

        seqno = 0
        msg = self.infile.read(500).decode()
        msg_type = None
        duplication_dict = {}
        while not msg_type == 'end':
            next_msg = self.infile.read(500).decode()

            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif next_msg == "":
                msg_type = 'end'

            packet = self.make_packet(msg_type,seqno,msg)
            self.send(packet.encode())
            #print("sent: %s" % packet)

            ########################################
            # your code should be able to handle packet 
            # 1. loss
            # 2. corruption
            # 3. duplication
            # 4. delay

            response = self.receive(1)

            while True:
                # loss
                if(response == None):
                    response = resend_packet(packet)
                    print("Packet Loss. Resend")
                    # continue

                # corruption
                elif (Checksum.validate_checksum(response.decode()) == False):
                    response = resend_packet(packet)
                    print("Checksum error. Resend")
                    # continue
                

                # duplication
                else:
                    resp_str = response.decode()
                    response_ack = resp_str.split('|')[1]
                    if(response_ack in duplication_dict):
                        print(f'Duplicate packet(seq no:{response_ack}) received. Resend')
                        response = resend_packet(packet)
                    else:
                        duplication_dict[response_ack] = 1
                        self.handle_response(resp_str)
                        # print(duplication_dict)
                        break
            
            ########################################

            msg = next_msg
            seqno += 1

        self.infile.close()
 

if __name__ == "__main__":
    def usage():
        print("BEARDOWN-TP Sender")
        print("-f FILE | --file=FILE The file to transfer; if empty reads from STDIN")
        print("-p PORT | --port=PORT The destination port, defaults to 33122")
        print("-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost")
        print("-d | --debug Print debug messages")
        print("-h | --help Print this usage message")

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:d", ["file=", "port=", "address=", "debug="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True

    s = Sender(dest,port,filename,debug)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
