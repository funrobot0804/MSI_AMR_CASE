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

from datetime import datetime
from AMR_CheckOccurV2 import *

IS_MODBUSTK_INSTALLED = False
try:
    import modbus_tk.modbus_tcp as mt
    import modbus_tk.defines as md
    IS_MODBUSTK_INSTALLED = True
except:
    pass




scriptName = "SecurityRangeDebug.py"

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

pause_range = float(sys.argv[1])
stop_range = float(sys.argv[2])


aco = AMR_CheckOccur("127.0.0.1")
aco.pause_range = pause_range
aco.stop_range = stop_range


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
now_ai_name = ai_name_prefix + f"SecurityRangeDebug,S0"
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
now_ai_name = ai_name_prefix + f"SecurityRangeDebug,S1"
aco.enable_detect_point(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++
                       

# ++++ Do whatever you want ++++
while(1):
    try:
        aco.get_detect_point()
        aco.pre_calculate_V2()
        aco.get_detect_point()
        result = aco.calculate_V2()
        break
    except:
        pass    

now = datetime.now()
date_time_str = now.strftime("%Y-%d-%m-%H-%M-%S")
fn = "/data/dump/" + "AMR_Cobot_Security_Debug_" + date_time_str + ".png"
aco.SaveDebugImage(fn)


# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ---- We must tell upper level program this mscript is finished normally before exiting. 
#      To do this, we put word "End" after "," (comma) in the end of ai_name. NOTICE: "E" of "End" must be upper case 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + f"SecurityRangeDebug,End"
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




