import sys
import time
import device
import requests
import json

ai_name_prefix = ""

me = device.robot("127.0.0.1")

def TurnOffCameraIR(name="xxx", t=-1):
    for trycount in range(1):
        map_arr = [0, 0, 0]

        x = 215.0
        y = 32.0
        a = 0.0

        url = "http://127.0.0.1:6660"+"/set_job"
        payload = { "set_job" : {
                        "name"  : name[0:1014],
                        "cmd"   : 302,
                        "map"   : map_arr, 
                        "target"  : [
                          {"x": float("%.2f"%x), "y": float("%.2f"%y), "a": float("%.2f"%a) }
                        ],
                        "data": ""
                    },
                 "mac": "e8:99:c4:c0:97:00"}

        if t > -1:
            payload['set_job']['time'] = int(t)

        r = requests.post(url, data=json.dumps(payload), timeout=2.0)
        if r.status_code!=200:
            print("====== {",sys._getframe().f_code.co_name,"} r.status_code!=200 ======")
            continue

        return r

    return None
    
    
now_ai_name = ai_name_prefix + "TurnOffCameraIR,S0"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)


TurnOffCameraIR(now_ai_name)
time.sleep(2.0)


now_ai_name = ai_name_prefix + "TurnOffCameraIR,End"
me.stop(now_ai_name)
while(1):
    misc = me.get_misc()
    if now_ai_name == misc["status"]["name"][0:len(now_ai_name)]:
        break
        
    time.sleep(0.2)
    