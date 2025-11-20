import threading
import time
import os
import socket
import subprocess
import pwd
import grp

import device
from PlcRollerRs485 import PlcRollerRs485

me = device.robot("127.0.0.1")

NO_PAUSE_YES_CONTINUE_AI_NAME_LIST = ["WaitTime",
                                      "WaitButton",
                                      "WaitExtInput",
                                      "WaitExtInputMuti",
                                      "WaitModbusMutiEqual",
                                      "WaitModbusSingleEqual"
                                      ]

NO_PAUSE_NO_CONTINUE_AI_NAME_LIST = ["Relocate",
                                     "SaveMap",
                                     "SetExtOutput",
                                     "SetExtOutputMuti",
                                     "SetModbus",
                                     "LoadMap"
                                     ]

NO_PAUSE_AI_NAME_LIST = NO_PAUSE_YES_CONTINUE_AI_NAME_LIST + NO_PAUSE_NO_CONTINUE_AI_NAME_LIST

hostPinger = device.Pinger()

LightStatus = [0, 0, 0]
pre_LightStatus = [0, 0, 0]


def Control_Up_Light_v2_dumb(color_list=[], switch_list=[], reason='none', isShowReason=False):
    pass


def Control_Up_Light_v2(color_list=[], switch_list=[], reason='none', isShowReason=False):
    global LightStatus

    sel_mask = [0, 0, 0, 0, 0, 0, 0, 0]
    io_mask = [0, 0, 0, 0, 0, 0, 0, 0]

    if ("red" in color_list) or ("Red" in color_list):
        sel_mask[0] = 1

    if ("yellow" in color_list) or ("Yellow" in color_list):
        sel_mask[1] = 1

    if ("green" in color_list) or ("Green" in color_list):
        sel_mask[2] = 1

    deceision = "None"
    for i, color in enumerate(color_list):
        if len(switch_list) > i:
            io_result = 0

            if ("red" == color) or ("Red" == color):
                LightStatus[0] = switch_list[i]
                deceision = "Red"

            if ("yellow" == color) or ("Yellow" == color):
                LightStatus[1] = switch_list[i]
                deceision = "Yellow"

            if ("green" == color) or ("Green" == color):
                LightStatus[2] = switch_list[i]
                deceision = "Green"

    if isShowReason == True:
        print("---------Control_Up_Light_v2----------")
        print("reason =", reason)
        print("deceision =", deceision)
        print("color_list =", color_list)
        print("switch_list =", switch_list)
        print("LightStatus =", LightStatus)
        print("--------------------------------------")


Control_Up_Light_v2 = Control_Up_Light_v2_dumb


def power_behavior():
    isReady = False
    pre_isCobotConnected = False
    cobot_disconnect_start_time = time.time()
    isPowerTurnOn = False

    last_battery_process_print_time = time.time()

    while (1):
        if time.time() - last_battery_process_print_time > 1.0:
            # print("# \"power_behavior\" processing... ,time={}".format(time.time()))
            last_battery_process_print_time = time.time()

        miscInfo = me.get_misc()

        isMiscReady = False
        if miscInfo is not None:
            isMiscReady = True

        position = None
        if isMiscReady == True:
            position = miscInfo['position']

        if isReady == False:
            if position is not None:
                lost_value = position['lost']
                if lost_value != 0:
                    isReady = True

        if isReady == True:
            if miscInfo['battery']['charging'] == 1:
                if isPowerTurnOn == False:
                    isPowerTurnOn = True

            elif miscInfo['battery']['charging'] == 0:
                if (miscInfo['battery']['power'] < 31) and (miscInfo['battery']['power'] > 0):
                    # mpg123_snd_pid = subprocess.Popen(
                    #     ["mpg123", "/data/etc/extra_ui/battery_below_30_percent_warning.mp3"], shell=False)
                    # mpg123_snd_pid.poll()
                    time.sleep(8.0)

        time.sleep(1.0)


isBackWalk = False
isPause = False


def back_walk_behavior():
    count = 0
    last_light_ctrl_time = time.time()
    while (1):
        if isBackWalk == True:
            if pre_isBackWalk == False:
                count = 0

            if time.time() - last_light_ctrl_time > 0.5:
                if count % 2 == 0:
                    Control_Up_Light_v2(["Green"], [0], "Back Walk Blink - Off")
                else:
                    Control_Up_Light_v2(["Green"], [1], "Back Walk Blink - On")

                count += 1

                if count > 29999:
                    count = 0

                last_light_ctrl_time = time.time()

        else:
            if isPause == True:
                Control_Up_Light_v2(["Green"], [0], "Green Pause")
            else:
                Control_Up_Light_v2(["Green"], [1], "Green No Pause")

        pre_isBackWalk = isBackWalk
        time.sleep(0.3)





# IPC parameters
SOCK_FILE = '/tmp/simple-ipc.socket'

# Setup socket
if os.path.exists(SOCK_FILE):
    os.remove(SOCK_FILE)

socket_s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
socket_s.bind(SOCK_FILE)
socket_s.listen(0)
socket_s.settimeout(0.1)

uid = pwd.getpwnam("pyuser").pw_uid
gid = grp.getgrnam("pyuser").gr_gid
while os.path.exists(SOCK_FILE)==True:
    os.chown(SOCK_FILE, uid, gid)
    break

socket_s_conn = None
socket_s_addr = None
socket_s_data = None

def SocketSafetySendAll(data):

    global socket_s_conn
    global socket_s_addr

    if socket_s_conn is not None:
        try:
            socket_s_conn.sendall(data)

        except Exception as e:
            print(f"socket_s_conn send Error! e={e}, str(e)={str(e)}, type(e)={type(e)}")

            socket_s_conn = None
            socket_s_addr = None


# Create threads
thread_b = threading.Thread(target=power_behavior)
thread_c = threading.Thread(target=back_walk_behavior)

# Run the thread
thread_b.start()
thread_c.start()

isReady = False
LifeCount = 0
pre_ext_io = None
before_start_time = -1

last_main_process_print_time = time.time()

prr = PlcRollerRs485()
prr.InitRs485()

if (prr.isFinish == 1):
    prr.SetReqState("RESET_ERROR")
    prr.SetAck(1)
    time.sleep(1.0)

while (1):
    prr.single_process()
    if prr.isFinish == 1:
        break

    time.sleep(0.1)

if (prr.isFinish == 1):
    prr.SetReqState("AUTO_MODE_ON")
    prr.SetAck(1)

while (1):
    prr.single_process()
    if prr.isFinish == 1:
        break

    time.sleep(0.1)

if (prr.isFinish == 1):
    prr.SetReqState("AUTO_MODE_OPERATION_REQ")
    prr.SetAck(1)
    time.sleep(1.0)

while (1):
    prr.single_process()
    if prr.isFinish == 1:
        break

    time.sleep(0.1)


if (prr.isFinish == 1):
    prr.SetReqState("INITIALIZE_MODE_ON")
    prr.SetAck(1)
    time.sleep(1.0)

while (1):
    prr.single_process()
    if prr.isFinish == 1:
        break

    time.sleep(0.1)

if (prr.isFinish == 1):
    prr.SetReqState("INITIALIZE_OPERATION_REQ")
    prr.SetAck(1)
    time.sleep(1.0)

while (1):
    prr.single_process()
    if prr.isFinish == 1:
        break

    time.sleep(0.1)

if (prr.isFinish == 1):
    prr.SetReqState("INITIALIZE_OPERATION_REQ_OFF")
    prr.SetAck(1)
    time.sleep(1.0)

while (1):
    prr.single_process()
    if prr.isFinish == 1:
        break

    time.sleep(0.1)

if (prr.isFinish == 1):
    prr.SetReqState("INITIALIZE_MODE_OFF")
    prr.SetAck(1)
    time.sleep(1.0)

while (1):
    prr.single_process()
    if prr.isFinish == 1:
        break

    time.sleep(0.1)

prr.ResetReqState()




while (1):

    isReady = False

    miscInfo = me.get_misc()
    isMiscReady = False
    if miscInfo is not None:
        isMiscReady = True

    position = None
    if isMiscReady == True:
        position = miscInfo['position']

    if isReady == False:
        if position is not None:
            lost_value = position['lost']
            if lost_value != 0:
                isReady = True

    if time.time() - last_main_process_print_time > 1.0:
        print("# \"main\" processing... ,time={}".format(time.time()))
        # print("# miscInfo =", miscInfo)
        last_main_process_print_time = time.time()

    if isReady == True:
        if LifeCount == 0:
            if miscInfo["status"]["status"] == 19:
                if miscInfo["status"]["info"] == 900:
                    if before_start_time <= -1:
                        before_start_time = time.time()

            if before_start_time > -1:
                if time.time() - before_start_time > 4.0:
                    # me.add_camera_ignore_area("Set Back Camera Ignore 2",2, -6.28, 6.28)
                    Control_Up_Light_v2(["Green", "Yellow", "Red"], [1, 0, 0], "Initial")
                    LifeCount += 1

        if "WaitButton" in miscInfo["status"]["name"]:
            if ("error," not in miscInfo["status"]["name"]) and \
                    ("youhavecontrol," not in miscInfo["status"]["name"]):
                pass
            else:
                pass

        else:
            if miscInfo["status"]["info"] == 12:
                Control_Up_Light_v2(["Yellow"], [1], "Yellow Pause")
            else:
                Control_Up_Light_v2(["Yellow"], [0], "Yellow No Pause")

        if miscInfo["status"]["info"] == 12:
            isPause = True
            isBackWalk = False

        else:
            isPause = False

            if type(miscInfo["status"]["data"]) is dict:
                if "@status_MD#" in list(miscInfo["status"]["data"].keys()):
                    if miscInfo["status"]["data"]["@status_MD#"] == -1:
                        isBackWalk = True
                    else:
                        isBackWalk = False

            else:
                isBackWalk = False

        isError = False
        if miscInfo["status"]["error"] != 0:
            isError = True
            Control_Up_Light_v2(["Red"], [1], "AI Error")

        if "error," in miscInfo["status"]["name"]:
            isError = True
            Control_Up_Light_v2(["Red"], [1], "FMS Error")

        if isError == False:
            Control_Up_Light_v2(["Red"], [0], "No FMS or AI Error")

        if pre_ext_io is not None:
            if (pre_ext_io[0] == 0) and \
                    (miscInfo["ext_io"][0] == 1):
                btn_list = miscInfo["btn"]
                btn_list[2] = btn_list[2] + 1
                me.set_button(btn_list)

                mpg123_snd_pid = subprocess.Popen(["mpg123", "/data/wav/button_push.mp3"], shell=False)

        pre_ext_io = miscInfo["ext_io"]

        # print(f"pre_LightStatus={pre_LightStatus}, LightStatus={LightStatus}")

        isAllLightSame = True
        for i, LS in enumerate(LightStatus):
            # print(f"i={i}, pre_LightStatus={pre_LightStatus}, LS={LS}")
            if pre_LightStatus[i] != LS:
                isAllLightSame = False
                break

        if isAllLightSame == False:
            sel_mask = [1, 1, 1, 0, 0, 0, 0, 0]
            io_mask = [0, 0, 0, 0, 0, 0, 0, 0]

            io_mask[0] = LightStatus[0]
            io_mask[1] = LightStatus[1]
            io_mask[2] = LightStatus[2]

            print("# Light Change - LightStatus =", LightStatus, "time =", time.time())

            me.set_misc(sel_mask, io_mask)

        for i, LS in enumerate(LightStatus):
            pre_LightStatus[i] = LS

        # Socket IPC part - Server
        try:
            # Accept 'request'
            if (socket_s_conn is None) and (socket_s_addr is None):
                socket_s_conn, socket_s_addr = socket_s.accept()
                socket_s_conn.settimeout(0.1)
                # print(f"type(socket_s_conn) = {type(socket_s_conn)}")
                # print(f"type(socket_s_addr) = {type(socket_s_addr)}")
                print(f'Connection by client, IP = {socket_s_addr}')


        except Exception as e:
            if type(e) is not socket.timeout:
                print(f"socket_s Error! e={e}, str(e)={str(e)}, type(e)={type(e)}")

        decode_socket_s_data = ""
        if socket_s_conn is not None:
            try:
                socket_s_data = socket_s_conn.recv(32)
                decode_socket_s_data = socket_s_data.decode('ascii')

            except Exception as e:
                if type(e) is not socket.timeout:
                    print(f"socket_s_conn recv Error! e={e}, str(e)={str(e)}, type(e)={type(e)}")
                    socket_s_conn = None
                    socket_s_addr = None

        if decode_socket_s_data != "":
            print(f"decode_socket_s_data = {decode_socket_s_data}")

        if type(socket_s_data) is bytes:
            socket_s_data = None

        if (prr.isFinish == 1) and (prr.req_state == 'STANDBY'):
            if decode_socket_s_data != "":
                decode_socket_s_data_slice = decode_socket_s_data.split(",")

                # print(f"decode_socket_s_data_slice = {decode_socket_s_data_slice}")

                if len(decode_socket_s_data_slice) == 1:
                    if decode_socket_s_data_slice[0] == "AUTO_MODE_ON":
                        prr.SetReqState("AUTO_MODE_ON")
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "AUTO_MODE_OPERATION_REQ":
                        prr.SetReqState("AUTO_MODE_OPERATION_REQ")
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "INITIALIZE_MODE_ON":
                        prr.SetReqState("INITIALIZE_MODE_ON")
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "INITIALIZE_OPERATION_REQ":
                        prr.SetReqState("INITIALIZE_OPERATION_REQ")
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "INITIALIZE_MODE_OFF":
                        prr.SetReqState("INITIALIZE_MODE_OFF")
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "INITIALIZE_OPERATION_REQ_OFF":
                        prr.SetReqState("INITIALIZE_OPERATION_REQ_OFF")
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "RESET_ERROR":
                        prr.SetReqState("RESET_ERROR")
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "DO_ACT":
                        prr.SetReqState("DO_ACT")
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "SLOT_1_REQ_OFF":
                        prr.SetReqState("SLOT_1_REQ_OFF")
                        prr.SetAck(1)
                        
                    elif decode_socket_s_data_slice[0] == "RESET_ERROR_DUMP_RP":
                        prr.SetReqState("RESET_ERROR_DUMP_RP")
                        prr.SetAck(1)    


                elif len(decode_socket_s_data_slice) >= 2:
                    if decode_socket_s_data_slice[0] == "SET_SLOT_ACT":
                        act_str = decode_socket_s_data_slice[1]
                        prr.SetReqState("SET_SLOT_ACT")
                        prr.SetReqData([act_str])
                        prr.SetAck(1)

                    elif decode_socket_s_data_slice[0] == "SET_SLOT":
                        slot_num = int(decode_socket_s_data_slice[1])
                        prr.SetReqState("SET_SLOT")
                        prr.SetReqData([slot_num])
                        prr.SetAck(1)


            else:
                if socket_s_conn is not None:
                    SocketSafetySendAll("Standby".encode('ascii'))


        prr.single_process()


        if (prr.isFinish == 0) and (prr.req_state != 'STANDBY'):
            if socket_s_conn is not None:
                SocketSafetySendAll("Busy".encode('ascii'))

        elif (prr.isFinish == 1) and (prr.req_state != 'STANDBY'):

            if prr.req_state != "ERROR":
                if socket_s_conn is not None:
                    SocketSafetySendAll("End".encode('ascii'))
            else:
                if socket_s_conn is not None:

                    if decode_socket_s_data != "":
                        decode_socket_s_data_slice = decode_socket_s_data.split(",")
                        # print(f"decode_socket_s_data_slice = {decode_socket_s_data_slice}")
                        if len(decode_socket_s_data_slice) == 1:
                            if decode_socket_s_data_slice[0] == "RESET_ERROR":
                                prr.SetReqState("RESET_ERROR")
                                prr.SetAck(1)

                    else:
                        SocketSafetySendAll("Fail".encode('ascii'))

        else:
            print(f"DEBUG - prr.isFinish={prr.isFinish}, prr.req_state={prr.req_state}")
            pass


        if "OK" in decode_socket_s_data:
            prr.ResetReqState()

        if "DISCONNECT" in decode_socket_s_data:
            SocketSafetySendAll("DISCONNECT".encode('ascii'))
            socket_s_conn = None
            socket_s_addr = None

        # print("=================")

    time.sleep(0.3)


print("End")
