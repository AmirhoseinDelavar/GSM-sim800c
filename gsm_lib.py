import serial
import time

# define serial port ( figure it out on device manager usb connected devices )
ser = serial.Serial('COM10', baudrate=9600, timeout=.1, rtscts=0)


# Utility function
def _send_command(com):
    com = com + "\r"
    com = com.encode()
    ser.write(com)
    time.sleep(0.1)
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
    if not ser.is_open:
        print("serial port is closed")
        ser.open()
    com = "ERROR"
    count = 0
    while "OK" not in com:
        com = _send_command("AT")
        time.sleep(0.1)
        count += 1
        if count > 5:
            print("Input Error " + str(com))
            return False

    # delete all msgs
    rep = _send_command("AT+CMGD=1,4")
    time.sleep(0.4)
    rep = _send_command("AT+CNMI=2,1,0,1,0")
    # time.sleep(0.15)
    return True


# send 'msg' to 'contact'
# phonenum = "+98-------"
def send_sms(phonenum, msg):
    rep = _send_command("AT+CMGF=1")
    time.sleep(0.1)
    rep = _send_command("AT+CSCS=\"GSM\"")
    time.sleep(0.2)
    rep = _send_command("AT+CSMP=17,167,0,0")
    time.sleep(0.2)
    rep = _send_command("AT+CMGS=\"" + phonenum + "\"")
    time.sleep(0.1)
    arr = bytearray(msg.encode())
    arr.extend(bytes.fromhex('1a'))
    rep = ser.write(arr)
    counter = 100
    while counter > 0:
        resp = ser.readline()
        if "+CMGS" in resp.decode():
            # message sent
            return True
        else:
            counter -= 1
    return False


# receive sms from 'contact'
def receiver_sms():
    sms_num = 0
    while True:
        text = ser.read_all().decode().strip()
        if "+CMTI" in text:
            print("msg received", text)
            # just received another sms with sms_num on sim-mem
            # +CMTI: "SM",1
            sms_num = text.split(sep=',')[1]
            _send_command("AT+CMGF=1")
            time.sleep(0.15)
            _send_command("AT+CSCS=\"UCS2\"")
            time.sleep(0.15)
            _send_command("AT+CSMP=17,167,0,0")
            time.sleep(0.15)
            rep = _send_command("AT+CMGR=" + sms_num)
            # time.sleep(2)
            # get body of msg with sms_num
            if "AT+CMGR=1" in rep:
                print("gettin request sms body", rep)
                phonenum = rep[1].split(',')[1].replace("\"", "")
                phonenum = phonenum.replace('00', '') # removes 00 hex characters
                phonenum = bytearray.fromhex(phonenum).decode(encoding="UTF-8").strip()

                msg_body = rep[-2]
                msg_body = msg_body.replace('00', '')
                msg_body = bytearray.fromhex(msg_body).decode(encoding="UTF-8").strip()

                print("phone:", type(phonenum))
                print("msg:", msg_body)
                # delete msg
                _send_command("AT+CMGD=" + sms_num)
                time.sleep(0.15)

