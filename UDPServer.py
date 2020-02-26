import struct
from socket import *
from socket import AF_INET
from socket import SOCK_DGRAM
import socket
# from socket import *
import hashlib
import threading
import time


class Ranger(object):
    def __init__(self, start_str, end_str):
        self._start_str = start_str
        self._end_str = end_str
        self._length = len(start_str)

    def _get_last_index_not_z(self, str_list):
        for i, char in enumerate(str_list[::-1]):
            if char != 'z':
                return self._length - 1 - i

    def _make_all_chars_after_index_into_a(self, str_list, index):
        for i in range(index + 1, self._length):
            str_list[i] = 'a'

    def generate_all_from_to_of_len(self):
        tmp = list(self._start_str)
        last = list(self._end_str)
        yield "".join(tmp)
        while tmp != last:
            i = self._get_last_index_not_z(tmp)
            tmp[i] = chr(ord(tmp[i]) + 1)
            if i is not len(tmp) - 1:
                self._make_all_chars_after_index_into_a(tmp, i)
            yield "".join(tmp)
        yield "".join(last)


def sha1(str):
    # encoding str using encode()
    # then sending to SHA1()
    return hashlib.sha1(str.encode())


def decoder_request(message):
    x1, temptype, x2, templength = struct.unpack_from('32s1c40s1c', message)  # unpack beginning of request message
    length = int.from_bytes(templength, byteorder='big')
    teamName, x3, hashStringtemp, x4, starttemp, endtemp = struct.unpack_from(
        '32s1c40s1c' + str(length) + 's' + str(length) + 's', message)  # unpack discover message
    start = starttemp.decode()
    end = endtemp.decode()
    hashString = hashStringtemp.decode()
    range = Ranger(start, end)
    print('start: ' + start + ' end: ' + end)
    for string in range.generate_all_from_to_of_len():
        sha = sha1(string).hexdigest()
        if sha == hashString:
            return encoder(4, string, hashString, teamName, length)
    return encoder(5, ' ', hashString, teamName, length)


def decoder(message):
    try:
        teamName, temp = struct.unpack_from('32s1c', message)  # unpack discover message
        type = int.from_bytes(temp, byteorder='big')
        if type == 1:
            return encoder(2, ' ', ' ', teamName, ' ')
        else:
            if type == 3:
                return decoder_request(message)
            else:
                print("the Type message is undefined")
                # return struct.pack('4s1c', bytes(str('none')), bytes(chr(2), 'utf-8'))
                return
    except:
        # return struct.pack('4s1c', bytes(str('none')), bytes(chr(2), 'utf-8'))
        return


def encoder(typy, answer, hashString, teamName, length):
    if typy == 2:  # OFFER
        message = struct.pack('32sc', bytes(str(teamName), 'utf-8'),
                              bytes(chr(2), 'utf-8'))  # offer message conatains: <teamname> <type = 1>
        return message
    if typy == 4:  # ACK
        print('sending ack')
        message = struct.pack('32sc40sc' + str(length) + 's', bytes(str(teamName), 'utf-8'), bytes(chr(4), 'utf-8'),
                              bytes(str(hashString), 'utf-8'), bytes(chr(length), 'utf-8'),
                              bytes(str(answer), 'utf-8'))
        return message
    if typy == 5:  # NACK
        print('sending nack')
        message = struct.pack('32sc40sc', bytes(str(teamName), 'utf-8'), bytes(chr(5), 'utf-8'),
                              bytes(str(hashString), 'utf-8'), bytes(chr(length), 'utf-8'))
        return message
    else:
        raise Exception("the Type message is undefined")


def handle_message(message, address):
    print('the server tries to handle a message')
    modifiedMessage = decoder(message)  # got an offer message ready to be sent
    # try:
    #     forcheck, x = struct.unpack_from('4s1c', modifiedMessage)
    #     temp = forcheck.decode()
    #     if temp == 'none':
    #         print('cannot understand the message')
    #         return
    try:
        serverSocket.sendto(modifiedMessage, address)  # send the offer message
        msg, clientAddress = serverSocket.recvfrom(2048)  # recieved request message
        answer_message = decoder(msg)
        serverSocket.sendto(answer_message, address)  # send the answer
    except:
        print('the server cannot handle this message')
        return


serverIP = socket.gethostbyname(socket.gethostname())
serverPort = 3117
listeningAddress = (serverIP, serverPort)
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(listeningAddress)
print("The server is ready to receive")
while 1:
    try:
        msg, clientAddress = serverSocket.recvfrom(2048)
        x = threading.Thread(target=handle_message, args=(msg, clientAddress))
        x.start()
    except:
        1

