# This mscript python file will show you how to write an appropriate mscript
#
# Usage of mscript in '/data/etc/extra_mscript':
#     Put this mission step in a mission - ["MissionScript", "Just_A_MScript", "EXTRA", ["-c","5"]]
#                                                                   ^             ^          ^
#                                                                  (a)           (b)        (c)
#
#                                        (a) The mscript's filename but without ".py" extension
#                                        (b) Means that use mscript in '/data/etc/extra_mscript'
#                                        (c) MScript's argument value
#
# The raised error message of mscript will show up in ".mlog" file. MScript error will make 'MissionScript' mission step fail. 

# ---- These 2 are MUST NEEDED libraries to import  
import device
import time
import os
import socket
import sys

# IPC parameters
SOCK_FILE = '/tmp/simple-ipc.socket'


# ---- This line is must needed. Variable name and its value must be the same 
#
#      ai_name_prefix = ""
#
#      Upper level program will change 'ai_name_prefix' value automatically to follow 
#      the mission script's step name rule

ai_name_prefix = ""



# ---- This line is also must needed. We need to change the ai_name especially when this mscript is end 
me = device.robot("127.0.0.1")


slot_num = int(sys.argv[1])
slot_act = str(sys.argv[2])
isFail = False

# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SlotAct,{slot_num},{slot_act},S0"
me.stop(now_ai_name)
print(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++
                       

# ++++ Do whatever you want ++++            
# Init socket object
if not os.path.exists(SOCK_FILE):
    me.stop("error,SlotAct_SockFileNotExists")
    os._exit(1)


client_s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client_s.connect(SOCK_FILE)
client_s.settimeout(0.1)


# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SlotAct,{slot_num},{slot_act},S1"
me.stop(now_ai_name)
print(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++



# ++++ Do whatever you want ++++
str2send = "RESET_ERROR"
client_s.sendall(str2send.encode('ascii'))
time.sleep(0.3)
while(1):
    try:
        data = client_s.recv(32)
        print(f'# Received bytes: {repr(data)}')

        de_data = data.decode('ascii')

        if de_data == "Standby":
            client_s.sendall("OK".encode('ascii'))
            time.sleep(0.5)
            break

        # elif de_data == "Fail":
        #     str2send = "DISCONNECT"
        #     client_s.sendall(str2send.encode('ascii'))
        #     isFail = True
        #
        # elif "DISCONNECT" in de_data:
        #     break

    except Exception as e:
        if type(e) is not socket.timeout:
            print(f"Error! e={e}, str(e)={str(e)}, type(e)={type(e)}")

if isFail == True:
    me.stop("error,SlotActError_ResetFail")
    os._exit(1)



# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SlotAct,{slot_num},{slot_act},S2"
me.stop(now_ai_name)
print(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++



# ++++ Do whatever you want ++++
str2send = "SLOT_1_REQ_OFF"
client_s.sendall(str2send.encode('ascii'))
time.sleep(0.3)
while (1):
    try:
        data = client_s.recv(32)
        print(f'# Received bytes: {repr(data)}')

        de_data = data.decode('ascii')

        if de_data == "End":
            client_s.sendall("OK".encode('ascii'))
            time.sleep(0.5)
            break


    except Exception as e:
        if type(e) is not socket.timeout:
            print(f"Error! e={e}, str(e)={str(e)}, type(e)={type(e)}")

if isFail == True:
    me.stop("error,SlotActError_SlotReqOffFail")
    os._exit(1)



# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SlotAct,{slot_num},{slot_act},S3"
me.stop(now_ai_name)
print(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++



# ++++ Do whatever you want ++++
str2send = "SET_SLOT" + "," + str(slot_num) + ","
client_s.sendall(str2send.encode('ascii'))
while(1):
    try:
        data = client_s.recv(32)
        print(f'# Received bytes: {repr(data)}')

        de_data = data.decode('ascii')

        if de_data == "End":
            client_s.sendall("OK".encode('ascii'))
            time.sleep(0.5)
            break

        elif de_data == "Fail":
            str2send = "DISCONNECT"
            client_s.sendall(str2send.encode('ascii'))
            isFail = True

        elif "DISCONNECT" in de_data:
            break

    except Exception as e:
        if type(e) is not socket.timeout:
            print(f"Error! e={e}, str(e)={str(e)}, type(e)={type(e)}")


if isFail == True:
    me.stop("error,SlotAct_SetSlotFail")
    os._exit(1)



# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SlotAct,{slot_num},{slot_act},S4"
me.stop(now_ai_name)
print(now_ai_name)
while (1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break

    time.sleep(0.2)
# ++++ END HERE ++++


# ++++ Do whatever you want ++++
str2send = "SET_SLOT_ACT" + "," + str(slot_act) + ","
client_s.sendall(str2send.encode('ascii'))
while (1):
    try:
        data = client_s.recv(32)
        print(f'# Received bytes: {repr(data)}')

        de_data = data.decode('ascii')

        if de_data == "End":
            client_s.sendall("OK".encode('ascii'))
            time.sleep(0.5)
            break

        elif de_data == "Fail":
            str2send = "DISCONNECT"
            client_s.sendall(str2send.encode('ascii'))
            isFail = True

        elif "DISCONNECT" in de_data:
            break


    except Exception as e:
        if type(e) is not socket.timeout:
            print(f"Error! e={e}, str(e)={str(e)}, type(e)={type(e)}")


if isFail == True:
    me.stop("error,SlotAct_SetActFail")
    os._exit(1)



# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SlotAct,{slot_num},{slot_act},S5"
me.stop(now_ai_name)
print(now_ai_name)
while (1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break

    time.sleep(0.2)
# ++++ END HERE ++++


# ++++ Do whatever you want ++++
str2send = "DO_ACT"
client_s.sendall(str2send.encode('ascii'))
while (1):
    try:
        data = client_s.recv(32)
        print(f'# Received bytes: {repr(data)}')

        de_data = data.decode('ascii')

        if de_data == "Standby":
            client_s.sendall("OK".encode('ascii'))
            time.sleep(0.5)
            break

        elif de_data == "Fail":
            str2send = "DISCONNECT"
            client_s.sendall(str2send.encode('ascii'))
            isFail = True

        elif "DISCONNECT" in de_data:
            break



    except Exception as e:
        if type(e) is not socket.timeout:
            print(f"Error! e={e}, str(e)={str(e)}, type(e)={type(e)}")



if isFail == True:
    me.stop("error,SlotAct_DoActFail")
    os._exit(1)


# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SlotAct,{slot_num},{slot_act},S6"
me.stop(now_ai_name)
print(now_ai_name)
while (1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break

    time.sleep(0.2)
# ++++ END HERE ++++


# ++++ Do whatever you want ++++
str2send = "DISCONNECT"
client_s.sendall(str2send.encode('ascii'))
time.sleep(2.0)


# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ---- We must tell upper level program this mscript is finished normally before exiting. 
#      To do this, we put word "End" after "," (comma) in the end of ai_name. NOTICE: "E" of "End" must be upper case 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SlotAct,{slot_num},{slot_act},End"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++  

# ---- Do remain works here, mscript is not really stopped or finished after changing ai_name with ",End" at tail 
# ---- Therefore, please remember DO NOT write a dummy python program that would not closed, 
#      it will consume AMR's memory and CPU resource




