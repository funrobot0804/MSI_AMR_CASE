import threading
import time
import os
import subprocess

import device

me = device.robot("127.0.0.1")

NO_PAUSE_YES_CONTINUE_AI_NAME_LIST = ["WaitTime",
                                      "WaitButton",
                                      "WaitExtInput",
                                      "WaitExtInputMuti",
                                      "WaitModbusMutiEqual",
                                      "WaitModbusSingleEqual"
                                      ]

NO_PAUSE_NO_CONTINUE_AI_NAME_LIST =  ["Relocate",
                                      "SaveMap",
                                      "SetExtOutput",
                                      "SetExtOutputMuti",
                                      "SetModbus",
                                      "LoadMap"
                                      ]

NO_PAUSE_AI_NAME_LIST = NO_PAUSE_YES_CONTINUE_AI_NAME_LIST + NO_PAUSE_NO_CONTINUE_AI_NAME_LIST

hostPinger = device.Pinger()

def Control_Up_Light(color_list=[], switch_list=[], reason='none', isShowReason=False):
    sel_mask = [0, 0, 0, 0, 0, 0, 0, 0]
    io_mask = [0, 0, 0, 0, 0, 0, 0, 0]
    
    if ("red" in color_list) or ("Red" in color_list):
        sel_mask[0] = 1

    if ("yellow" in color_list) or ("Yellow" in color_list):
        sel_mask[1] = 1
        
    if ("green" in color_list) or ("Green" in color_list):
        sel_mask[2] = 1
        
    for i, color in enumerate(color_list):    
        if len(switch_list) > i:
            io_result = 0
            if switch_list[i] > 0:
                if ("red" == color) or ("Red" == color):
                    io_mask[0] = switch_list[i]

                if ("yellow" == color) or ("Yellow" == color):
                    io_mask[1] = switch_list[i]
        
                if ("green" == color) or ("Green" == color):
                    io_mask[2] = switch_list[i]

    if isShowReason == True:
        print("---------Control_Up_Light----------")
        print("reason =", reason)
        print("sel_mask =", sel_mask)
        print("io_mask =", io_mask)    
    
    me.set_misc(sel_mask, io_mask)
    
    #time.sleep(0.5)


def power_behavior():
    isReady = False
    pre_isCobotConnected = False
    cobot_disconnect_start_time = time.time()
    isPowerTurnOn = False
    while(1):
        print("# \"power_behavior\" processing... ,time={}".format(time.time()))

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
                if lost_value!=0:
                    isReady = True

        if isReady == True:
            if miscInfo['battery']['charging'] == 1:
                if isPowerTurnOn == False:
                    print("# \"power_behavior\" Turn On Power !")
                    isPowerTurnOn = True    

            elif miscInfo['battery']['charging'] == 0:
                if (miscInfo['battery']['power'] < 31) and (miscInfo['battery']['power'] > 0):
                    mpg123_snd_pid = subprocess.Popen(["mpg123", "/data/etc/extra_ui/battery_below_30_percent_warning.mp3"], shell=False)
                    #mpg123_snd_pid.poll()
                    time.sleep(8.0)
            

        time.sleep(1.0)



isBackWalk = False
isPause = False
def back_walk_behavior():
    count = 0
    last_light_ctrl_time = time.time()
    while(1):
        if isBackWalk == True:
            if pre_isBackWalk == False:
                count = 0

            if time.time() - last_light_ctrl_time > 0.5:
                if count%2 == 0:
                    Control_Up_Light(["Green"],[0], "Back Walk Blink - Off")
                else:
                    Control_Up_Light(["Green"],[1], "Back Walk Blink - On")

                count += 1
                
                if count > 29999:
                    count = 0
                    
                last_light_ctrl_time = time.time()    
        
        else:
            if isPause == True:
                Control_Up_Light(["Green"],[0], "Green Pause")
            else:
                Control_Up_Light(["Green"],[1], "Green No Pause")
                
  
        
        
        pre_isBackWalk = isBackWalk
        time.sleep(0.3)
                

# Create threads
thread_b = threading.Thread(target = power_behavior)
thread_c = threading.Thread(target = back_walk_behavior)

# Run the thread
thread_b.start()
thread_c.start()
            


isReady = False
LifeCount = 0
pre_ext_io = None
before_start_time = -1
while(1):
    isReady = False

    print("# \"main\" processing... ,time={}".format(time.time()))

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
            if lost_value!=0:
                isReady = True
        
    if isReady == True:
        if LifeCount == 0:
            if miscInfo["status"]["status"] == 19:
                if miscInfo["status"]["info"] == 900:
                    if before_start_time <= -1:
                        before_start_time = time.time()    
            
            if before_start_time > -1:    
                if time.time() - before_start_time > 4.0:
                    #me.add_camera_ignore_area("Set Back Camera Ignore 2",2, -6.28, 6.28)
                    Control_Up_Light(["Green", "Yellow", "Red"], [1,0,0], "Initial")
                    LifeCount += 1


        if "WaitButton" in miscInfo["status"]["name"]:
            if ("error," not in miscInfo["status"]["name"]) and \
               ("youhavecontrol," not in miscInfo["status"]["name"]):
                Control_Up_Light(["Yellow"],[1], "WaitButton")
            else:
                Control_Up_Light(["Yellow"],[0], "No WaitButton")
                
        else:
            if miscInfo["status"]["info"] == 12:
                Control_Up_Light(["Yellow"],[1], "Yellow Pause")
            else:
                Control_Up_Light(["Yellow"],[0], "Yellow No Pause")
            
            
        if miscInfo["status"]["info"] == 12:
            isPause = True
            isBackWalk = False
            
        else:
            isPause = False
            
            if miscInfo["status"]["data"]["@status_MD#"] == -1:
                isBackWalk = True
            else:
                isBackWalk = False
        

        

        isError = False        
        if miscInfo["status"]["error"]!=0:
            isError = True
            Control_Up_Light(["Red"],[1], "AI Error")

                
        if "error," in miscInfo["status"]["name"]:    
            isError = True
            Control_Up_Light(["Red"],[1], "FMS Error")
            
        if isError == False:
            Control_Up_Light(["Red"],[0], "No FMS or AI Error")
            
         
        if  pre_ext_io is not None:   
            if  (pre_ext_io[0] == 1) and \
                (miscInfo["ext_io"][0] == 0):
                btn_list = miscInfo["btn"]
                btn_list[2] = btn_list[2] + 1
                me.set_button(btn_list)
                
                mpg123_snd_pid = subprocess.Popen(["mpg123", "/data/wav/button_push.mp3"], shell=False)


        pre_ext_io = miscInfo["ext_io"]

    time.sleep(0.3)



print("End")
