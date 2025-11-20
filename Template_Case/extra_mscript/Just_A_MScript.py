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



# ---- This line is must needed. Variable name and its value must be the same 
#
#      ai_name_prefix = ""
#
#      Upper level program will change 'ai_name_prefix' value automatically to follow 
#      the mission script's step name rule

ai_name_prefix = ""



# ---- This line is also must needed. We need to change the ai_name especially when this mscript is end 
me = device.robot("127.0.0.1")



# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + "Just_A_MScript,S0"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++
                       

# ++++ Do whatever you want ++++            
           

# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We can use ai_name with "S0", "S1", "S2"... after "," (comma) to track mscript process as a step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + "Just_A_MScript,S1"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
# ++++ END HERE ++++



# ++++ Do whatever you want ++++ 



# ---- Lines below show you how to change ai_name and check the ai_name is really changed and we can do the next step 
# ---- We suggest to put mscript filename without extension before "," (comma) that user can know that mscript is running correctly 
#
# ---- We must tell upper level program this mscript is finished normally before exiting. 
#      To do this, we put word "End" after "," (comma) in the end of ai_name. NOTICE: "E" of "End" must be upper case 
#
# ++++ START HERE ++++
now_ai_name = ai_name_prefix + "Just_A_MScript,End"
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




