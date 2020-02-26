import struct
import socket
from socket import *
import threading
import time

counter_ack = 0


def decoder(message, hashString, length, start, end):  # message in still packed
    tempteamName, temptype = struct.unpack_from('32sc', message)
    teamName = str(tempteamName)
    type = int.from_bytes(temptype, byteorder='big')
    if type == 2:
        return encoder_request(hashString, length, teamName, 3, start, end)
    elif type == 4:
        x1, x2, x3, x4, tempanswer = struct.unpack_from('32sc40sc' + str(length) + 's', message)
        answer = tempanswer.decode()
        global counter_ack
        counter_ack = counter_ack + 1
        print('The input string is ' + answer)
        return ''
    elif type == 5:
        return ''
    else:
        print('wrong type')
        return ''

def encoder_request(hashString, length, teamName, type, start, end):
    while len(hashString) < 40:
        hashString = "0" + hashString
    message = struct.pack('32s1c40s1c' + str(length) + 's' + str(length) + 's', bytes(str(teamName), 'utf-8'),
                          bytes(chr(type), 'utf-8'), bytes(str(hashString), 'utf-8'),
                          bytes(chr(length), 'utf-8'), bytes(str(start), 'utf-8'), bytes(str(end), 'utf-8'))
    return message


# returns array of strings- every two cells are the range of one server
def divide_two_domains(len, num_of_servers):
    domains = [None] * num_of_servers * 2
    first = ""
    last = ""
    i = 0
    while i < len:
        first = first + 'a'  # aaa
        last = last + 'z'  # zzz
        i = i + 1
    total = convert_string_to_int(last)
    per_server = total / num_of_servers
    domains[0] = first
    domains[domains.__len__() - 1] = last
    sum = 0
    j = 1
    while j <= domains.__len__() - 2:
        sum = sum + per_server
        domains[j] = convert_int_to_string(sum, len)  # end domain of server
        sum = sum + 1
        domains[j + 1] = convert_int_to_string(sum, len)  # start domain of next server
        j = j + 2
    return domains


def convert_string_to_int(str):
    char_array = split(str)
    num = 0
    for c in char_array:
        if c < 'a' or c > 'z':
            raise RuntimeError("invalid")
        num = num * 26
        num = num + ord(c) - 97
    return num


def convert_int_to_string(to_convert, length):
    s = ""
    while to_convert > 0:
        c = int(to_convert % 26)
        s = chr(c + 97) + s
        to_convert = int(to_convert / 26)
        length = length - 1
    while length > 0:
        s = 'a' + s
        length = length - 1
    return s


def split(word):
    return [char for char in word]


def handle_message(teamName, hashString, length, start, end, serverAddress):
    mess = struct.pack('32s1c', bytes(teamName, 'utf-8'), bytes(chr(2), 'utf-8'))  # a fake offer, just to make it work
    message = decoder(mess, hashString, length, start, end)  # request message, already packed
    #message = struct.pack('30s', bytes('blabla', 'utf-8'))
    clientSocket.sendto(message, serverAddress)
    clientSocket.settimeout(60)  # 1 second to recieve message
    try:
        msg, serverAddress = clientSocket.recvfrom(2048)  # suppose to be ack/nack
        new_message = decoder(msg, hashString, length, start, end)
    except error:
        return



################################ main #######################################
numOfServers = 0
addressQueue = []
threadPool = []
serverName = ''
serverPort = 3117
teamName = "00000000000000000000000000000S&S"
clientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
hashString = input('Welcome to S&S. Please enter the hash:')
# hashString = '422ab519eac585ef4ab0769be5c019754f95e8dc' #tashaf
# hashString = '86f7e437faa5a7fce15d1ddcb9eaeaea377667b8'  # a
length = int(input('Please enter the input string length:'))
message = struct.pack('32s1c', bytes(str(teamName), 'utf-8'), bytes(chr(1), 'utf-8'))  # discover message
clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
clientSocket.sendto(message, ('<broadcast>', 3117))  # send broadcast

TIMEOUT_WAIT = 5
timeout = time.time() + TIMEOUT_WAIT
clientSocket.settimeout(5)  # 1 second to wait for offer from servers
while time.time() < timeout:
    try:
        temp_message, serverAddress = clientSocket.recvfrom(2048)
        numOfServers = numOfServers + 1
        addressQueue.append(serverAddress)
    except error:
        break

if (numOfServers == 0):
    print('couldnt find servers')
    clientSocket.close()
    exit(0)

arr = divide_two_domains(int(length), numOfServers)
i = 0
while i < len(arr):
    add = addressQueue.pop()
    start = arr[i]
    end = arr[i + 1]
    i = i + 2
    x = threading.Thread(target=handle_message, args=(teamName, hashString, length, start, end, add))
    x.start()
    threadPool.append(x)

for t in threadPool:
    t.join()

if counter_ack == 0:
    print('couldnt find the answer')

clientSocket.close()
