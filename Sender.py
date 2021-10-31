# import sys
# import getopt
# import time
# import random
# import os
# import math

# import Checksum
# import BasicSender

# # initial commit

# '''
# This is a skeleton sender class. Create a fantastic transport protocol here.
# '''
# class Sender(BasicSender.BasicSender):
#     def __init__(self, dest, port, filename, debug=False):
#         super(Sender, self).__init__(dest, port, filename, debug)

#     def handle_response(self,response_packet):
#         if Checksum.validate_checksum(response_packet):
#             print("recv: %s" % response_packet)
#             return False
#         else:
#             print("recv: %s <--- CHECKSUM FAILED" % response_packet)
#             return True

#     # Main sending loop.
#     def start(self):
#         # corruption_flag = True
#         seqno = 0
#         msg = self.infile.read(500).decode()
#         next_msg = self.infile.read(500).decode()
#         # corruption_flag = True
#         msg_type = None
#         duplication_dict ={}
#         while not msg_type == 'end':
#             # msg_type = 'data'
#             # next_msg = self.infile.read(500).decode()

#             msg_type = 'data'
#             if seqno == 0:
#                 msg_type = 'start'
#             elif next_msg == "":
#                 msg_type = 'end'

#             packet = self.make_packet(msg_type,seqno,msg)
#             self.send(packet.encode())
#             # print("sent: %s" % packet)

#             ##### your code goes here ... #####
#             # your code should be able to handle packet 
#             # 1. loss
#             # 2. corruption
#             # 3. duplication
#             # 4. delay
#             # add new functions as necessary

#             # the receiver has issues, in the basic sender this takes a timeout parameter; which we can use; setting it to 2 seconds
#             # 1. loss
#             response = self.receive(1)
#             while response == None:
#                 self.send(packet.encode())
#                 response = self.receive(1)

#             resp_str = response.decode()
#             corruption_flag = self.handle_response(resp_str)
#             response_ack = resp_str.split('|')[1]

#             # if response_ack not in duplication_dict:
#             #     duplication_dict[response_ack] = 1
#             # else:
#             #     print("Duplicate data")

#             if (not corruption_flag) and (response_ack not in duplication_dict):
#                 msg = next_msg
#                 seqno += 1
#                 next_msg = self.infile.read(500).decode()
#                 duplication_dict[response_ack] = 1
#             else:
#                 # next_msg = msg
#                 print("Duplicate")


#         print(duplication_dict)
#         self.infile.close()
 

# '''
# This will be run if you run this script from the command line. You should not
# change any of this; the grader may rely on the behavior here to test your
# submission.
# '''
# if __name__ == "__main__":
#     def usage():
#         print("BEARDOWN-TP Sender")
#         print("-f FILE | --file=FILE The file to transfer; if empty reads from STDIN")
#         print("-p PORT | --port=PORT The destination port, defaults to 33122")
#         print("-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost")
#         print("-d | --debug Print debug messages")
#         print("-h | --help Print this usage message")

#     try:
#         opts, args = getopt.getopt(sys.argv[1:],
#                                "f:p:a:d", ["file=", "port=", "address=", "debug="])
#     except:
#         usage()
#         exit()

#     port = 33122
#     dest = "localhost"
#     filename = None
#     debug = False

#     for o,a in opts:
#         if o in ("-f", "--file="):
#             filename = a
#         elif o in ("-p", "--port="):
#             port = int(a)
#         elif o in ("-a", "--address="):
#             dest = a
#         elif o in ("-d", "--debug="):
#             debug = True

#     s = Sender(dest,port,filename,debug)
#     try:
#         s.start()
#     except (KeyboardInterrupt, SystemExit):
#         exit()

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
        duplication_dict ={}
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
                    continue

                # corruption
                elif (Checksum.validate_checksum(response.decode()) == False):
                    print("Checksum error. Resend")
                    response = resend_packet(packet)
                    continue
                

                # duplication
                elif(response != None):
                    resp_str = response.decode()
                    response_ack = resp_str.split('|')[1]
                    if(response_ack in duplication_dict):
                        print(f'Duplicate packet(seq no:{response_ack}) received. Resend')
                        response = resend_packet(packet)
                    else:
                        duplication_dict[response_ack] = 1
                        print(duplication_dict)
                        break
            
            resp_str = response.decode()
            self.handle_response(resp_str)
            print(duplication_dict)
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
