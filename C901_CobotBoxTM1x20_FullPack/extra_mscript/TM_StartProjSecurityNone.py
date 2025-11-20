# This mscript python file will show you how to write an apporiate mscript
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
import threading
import subprocess
import sys
import os

from AMR_CheckOccurV2 import *

IS_MODBUSTK_INSTALLED = False
try:
    import modbus_tk.modbus_tcp as mt
    import modbus_tk.defines as md
    IS_MODBUSTK_INSTALLED = True
except:
    pass




scriptName = "TM_StartProj.py"

def syncprint(scriptName,status,info,name,M):
    print(scriptName,",",status,",",info,",",name,",",M,",",time.time(),",", sep='', flush=True)

def fix_ai_status_string(r_status):
    tmp_aistatus = r_status
    tmp_aistatus.pop("data", None)
    fix_aistatus_str = str(tmp_aistatus).replace(",", "|")
    return fix_aistatus_str




# ---- This line is must needed. Variable name and its value must be the same 
#
#      ai_name_prefix = ""
#
#      Upper level program will change 'ai_name_prefix' value automatically to follow 
#      the mission script's step name rule

ai_name_prefix = ""



# ---- This line is also must needed. We need to change the ai_name especially when this mscript is end 
me = device.robot("127.0.0.1")


proj_name = sys.argv[1]
pause_range = float(sys.argv[2])
stop_range = float(sys.argv[3])


aco = AMR_CheckOccur("127.0.0.1")
aco.pause_range = pause_range
aco.stop_range = stop_range

the_modbus_master = mt.TcpMaster("192.168.88.7", 502)
the_modbus_master.set_timeout(120.0)
the_modbus_master.set_verbose(True)


playsound_thread = None
def PlaySound(filepath=""):
    mpg123_snd_pid = subprocess.Popen(["mpg123",filepath],shell=False)
    while(1):
        if mpg123_snd_pid.poll() is not None:
            break

        time.sleep(0.2)



# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"TM_StartProj,{proj_name},S0"
me.stop(now_ai_name)
while (1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break

    time.sleep(0.2)
# ++++ END HERE ++++


# ++++ Do whatever you want ++++
aco.get_map_info()
aco.get_misc()

while(aco.isGetFixedMapSuccess == 0):
    aco.get_fixed_map()
    time.sleep(1.0)

me.stop(now_ai_name)
while (1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        if misc["status"]["status"] == 19:
            break

    time.sleep(0.2)




# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"TM_StartProj,{proj_name},S1"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++
                       

# ++++ Do whatever you want ++++            
           
st_addr = 7701
output_value = []
tmp_str = ""
for i, c in enumerate(proj_name):
    #hex_value = int(hex(ord(c)),16)
    
    print(f"# i={i}, c={c}")
    
    tmp_str += str(c)
    print("A. tmp_str =", tmp_str)
    
    if i>0:        
        if i!=len(proj_name)-1:
            if (i+1)%2==0:
                print("B. tmp_str =", tmp_str)
                hex_value = int.from_bytes(bytes(tmp_str.encode('ascii')), "big")
                output_value.append(hex_value)
                tmp_str = ""
            
        if i==len(proj_name)-1:
            if len(tmp_str)==2:
                pass
            
            elif len(tmp_str)==1:
                tmp_str += "\x00"  
            
            print("C. tmp_str =", tmp_str)
            
            hex_value = int.from_bytes(bytes(tmp_str.encode('ascii')), "big")
            output_value.append(hex_value)
            tmp_str = ""
    

hex_value = int.from_bytes(b'\x00\x00', "big")
output_value.append(hex_value)

quantity = len(output_value)    

ret = the_modbus_master.execute(1, md.WRITE_MULTIPLE_REGISTERS, \
                          starting_address=st_addr, \
                          quantity_of_x=quantity, \
                          output_value=output_value)

print("7701 ret=", ret, "quantity =", quantity)

# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"TM_StartProj,{proj_name},S2"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++
                       

# ++++ Do whatever you want ++++            
           
st_addr = 7104
output_value = 1
quantity = 1    

ret = the_modbus_master.execute(1, md.WRITE_SINGLE_COIL, \
                          starting_address=st_addr, \
                          quantity_of_x=quantity, \
                          output_value=output_value)


print("7104 ret=", ret)


# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"TM_StartProj,{proj_name},S3"
aco.enable_detect_point(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++
                       

# ++++ Do whatever you want ++++            
counter = 0
is_people_pause_now = 0
time.sleep(1.0)            
aistatus = ""
ainame = ""
is_already_init = 0
now_time = time.time()
while(1):
    try:

        misc = me.get_misc()

        if misc is not None:
            if "status" in misc.keys():
                aistatus = fix_ai_status_string(misc)
                aistatus = ""
                ainame = misc["status"]["name"]


        btn_press_list =  the_modbus_master.execute(1, \
                                            md.READ_DISCRETE_INPUTS, \
                                            starting_address=7150, \
                                            quantity_of_x=6)

        btn_stop_val = btn_press_list[3]


        status_list = the_modbus_master.execute(1, \
                                        md.READ_DISCRETE_INPUTS, \
                                        starting_address=7201, \
                                        quantity_of_x=10)

        #print(f"status_list = {status_list}")
        #print(f"btn_press_list = {btn_press_list}")
        #print("----------")

        error_val = status_list[0]
        stop_val = status_list[1]
        estop_val = status_list[7]
        isautoremote_val = status_list[9]

        if error_val == 1:
            print("Error")
            me.stop("error,TM_StartProj_Error")
            os._exit(1)

        # if isautoremote_val == 0:
            # print("NoAutoRemote")
            # me.stop("error,TM_StartProj_NoAutoRemote")
            # os._exit(1)

        if estop_val == 1:
            print("EStopTrigger")
            me.stop("error,TM_StartProj_EStopTrigger")
            os._exit(1)

        if btn_stop_val == 1:
            print("StopBtnTrigger")
            me.stop("error,TM_StartProj_StopBtnTrigger")
            os._exit(1)

        # Normal End
        if stop_val == 0:
            if time.time() - now_time > 3.0:
                print("NormalEnd")
                break

        time.sleep(0.2)

    except:
        time.sleep(0.2)
        



# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ---- We must tell upper level program this mscript is finished normally before exiting. 
#      To do this, we put word "End" after "," (comma) in the end of ai_name. NOTICE: "E" of "End" must be upper case 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"TM_StartProj,{proj_name},End"
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




