import device
import time
import os
import sys
import threading
import ecam_mgr
    
fed_guid = sys.argv[1]

ai_name_prefix = ""


missioncount = 0

me = device.robot("127.0.0.1")        
                    

now_ai_name = ai_name_prefix + str(fed_guid) + ",Start"
print(f"#{now_ai_name}")
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break          
    else:
        print("# ai_name is not the same, time =", time.time())
        print("# now_ai_name = {n}".format(n=now_ai_name))
        print("# misc[\"status\"][\"name\"][0:len(now_ai_name)] = {n}".format(n=misc["status"]["name"][0:len(now_ai_name)]))
        
    time.sleep(0.2)


ecm = ecam_mgr.ECameraStreamingHelper()


# ====================================

now_ai_name = ai_name_prefix + str(fed_guid) + ",Running"
print(f"#{now_ai_name}")
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break          
    else:
        print("# ai_name is not the same, time =", time.time())
        print("# now_ai_name = {n}".format(n=now_ai_name))
        print("# misc[\"status\"][\"name\"][0:len(now_ai_name)] = {n}".format(n=misc["status"]["name"][0:len(now_ai_name)]))
        
    time.sleep(0.2)


          
result = ecm.stop_ecam_streaming()
                      
                 


# ===================================

if (result!=0):
    print(f"# {fed_guid},Error,{result}")

    now_ai_name = ai_name_prefix + str(fed_guid) + ",Error" + str(result)
    print(f"#{now_ai_name}")
    me.stop(now_ai_name)
    while(1):
        misc = me.get_misc()
        if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
            break          
        else:
            print("# ai_name is not the same, time =", time.time())
            print("# now_ai_name = {n}".format(n=now_ai_name))
            print("# misc[\"status\"][\"name\"][0:len(now_ai_name)] = {n}".format(n=misc["status"]["name"][0:len(now_ai_name)]))
            
        time.sleep(0.2)
       

else:
    print(f"# {fed_guid},End")

    now_ai_name = ai_name_prefix + str(fed_guid) + ",End"
    print(f"#{now_ai_name}")
    me.stop(now_ai_name)
    while(1):
        misc = me.get_misc()
        if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
            break          
        else:
            print("# ai_name is not the same, time =", time.time())
            print("# now_ai_name = {n}".format(n=now_ai_name))
            print("# misc[\"status\"][\"name\"][0:len(now_ai_name)] = {n}".format(n=misc["status"]["name"][0:len(now_ai_name)]))
            
        time.sleep(0.2)
        
        
sys.exit(0) 

