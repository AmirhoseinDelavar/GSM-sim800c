import serial
import time

ser = serial.Serial('COM8', baudrate=9600, timeout=.1, rtscts=0)
PhoneNo = "+98-------"
Message = "test"


def sendCommand(com):
    com = com + "\r"
    com = com.encode()
    ser.write(com)
    # time.sleep(2)
    ret = []
    while ser.inWaiting() > 0:
        msg = ser.readline().decode().strip()
        # msg = ser.readline().decode()
        msg = msg.replace("\r", "")
        # msg = msg.replace("\n", "")
        if msg != "":
            ret.append(msg)
    return ret


# init sms unit
def start_gsm():
    com = "ERROR"
    count = 0
    while com != "OK":
        com = sendCommand("AT")[1]
        count += 1
        if count > 5:
            print("COULD NOT GET A HELLO, all I got was " + com)
            return False

    # delete all msgs
    rep = sendCommand("AT+CMGD=1,4")
    time.sleep(0.5)
    rep = sendCommand("AT+CNMI=2,1,0,1,0")
    time.sleep(0.15)
    return True


# send 'msg' to 'contact'
def send_sms(phonenum, msg):
    rep = sendCommand("AT+CMGF=1")
    time.sleep(0.1)
    rep = sendCommand("AT+CSCS=\"GSM\"")
    time.sleep(0.3)
    rep = sendCommand("AT+CSMP=17,167,0,0")
    time.sleep(0.3)
    rep = sendCommand("AT+CMGS=\"" + phonenum + "\"")
    time.sleep(0.1)
    arr = bytearray(msg.encode())
    arr.extend(bytes.fromhex('1a'))
    rep = ser.write(arr)
    counter = 100
    while counter > 0:
        resp = ser.readline()
        if "+CMGS" in resp.decode():
            return True
        else:
            counter -= 1


# receive sms from 'contact'
def receiver_sms():
    sms_num = 0
    while True:
        text = ser.read_all().decode().strip()
        if "+CMTI" in text:
            print("msg received")
            # just received another sms
            # +CMTI: "SM",1
            sms_num = text.split(sep=',')[1]
            sendCommand("AT+CMGF=1")
            time.sleep(0.15)
            sendCommand("AT+CSCS=\"UCS2\"")
            time.sleep(0.15)
            sendCommand("AT+CSMP=17,167,0,0")
            time.sleep(0.15)
            sendCommand("AT+CMGR=" + sms_num)
            time.sleep(2)
        elif "+CMGR" in text:
            print("gettin request sms body")
            phonenum = text.split(',')[1].replace("\"", "")
            phonenum = bytearray.fromhex(phonenum).decode()

            msg_body = text.split(',')[4].replace("\"", "").split()[1]
            msg_body = bytearray.fromhex(msg_body).decode()

            # delete msg
            sendCommand("AT+CMGD=" + sms_num)
            time.sleep(0.15)

            # add to db
            #add_msg_db(phonenum, msg_body)


# add 'msg' from 'contact' to database
#def add_msg_db(phonenum, msg_body):
#    pass


#receiver_sms()
