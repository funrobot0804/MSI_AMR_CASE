import time

import device


ai_name_prefix = ""

me = device.robot("127.0.0.1")

now_ai_name = ai_name_prefix + "CxlBackCamera,S0"

me.add_camera_ignore_area(now_ai_name, 2, -6.28, 6.28)

time.sleep(0.5)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        if miscInfo["status"]["status"] == 19:
            if miscInfo["status"]["info"] == 900:    
                break
        
    time.sleep(0.2)
           


now_ai_name = ai_name_prefix + "CxlBackCamera,End"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
  
    