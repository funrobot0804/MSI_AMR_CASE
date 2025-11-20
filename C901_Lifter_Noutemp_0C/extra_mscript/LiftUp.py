import time

import device


ai_name_prefix = ""

me = device.robot("127.0.0.1")

now_ai_name = ai_name_prefix + "LiftUp,S0"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
            
me.set_internal_misc([0,1,0,0,0,0,0,0],\
                     [0,1,0,0,0,0,0,0] )            
            
time.sleep(2.0)            

now_ai_name = ai_name_prefix + "LiftUp,S1"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)

me.set_misc([1,0,0,0,0,0,0,0],\
            [1,0,0,0,0,0,0,0] )

time.sleep(2.0)

now_ai_name = ai_name_prefix + "LiftUp,S2"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        if misc["ext_io"][1] == 0:
            break
        else:
            print("# misc[\"ext_io\"][1] is not 0, time =", time.time())
            print("# misc[\"ext_io\"][1] =", misc["ext_io"][1])            
    else:
        print("# ai_name is not the same, time =", time.time())
        print("# now_ai_name = {n}".format(n=now_ai_name))
        print("# misc[\"status\"][\"name\"][0:len(now_ai_name)] = {n}".format(n=misc["status"]["name"][0:len(now_ai_name)]))
        
    time.sleep(0.2)

me.set_internal_misc([0,1,0,0,0,0,0,0],\
                     [0,0,0,0,0,0,0,0] )

time.sleep(2.0)

now_ai_name = ai_name_prefix + "LiftUp,End"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
  
    