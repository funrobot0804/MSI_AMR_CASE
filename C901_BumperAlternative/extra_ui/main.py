import threading
import time
import os
import subprocess

import device

proc = subprocess.Popen(['sh', '/data/etc/extra_ui/openport.sh'])

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

# Thread for extra bumper behavior
def extra_bump_behavior():
    isReady = False
    status = "Normal"
    pre_status = "Normal"
    next_status = "Normal"
    touch_state_change_start_time = time.time()
    touch_state_history_list = []
    touch_period_history_list = []
    pre_touch_state = 0
  
    while(1):
        print("# \"extra_bump_behavior\" processing... ,time={}".format(time.time()))
        
        
        miscInfo = me.get_misc()
        isMiscReady = False
        isReady = False
        
        if miscInfo is not None:
            isMiscReady = True
        else:
            print(f"# \"extra_bump_behavior\" miscInfo is None")    
        
        position = None
        if isMiscReady == True:
            position = miscInfo['position']
        else:
            print(f"# \"extra_bump_behavior\" isMiscReady == False")

        if isReady == False:
            if position is not None:
                lost_value = position['lost']
                if lost_value!=0:
                    isReady = True
        
        print(f"# \"extra_bump_behavior\" isReady == {isReady}")
            
        if isReady == True:
            # Update Start Time when Touch State is Changed
            if miscInfo['ext_io'][0] != pre_touch_state:
                touch_state_change_start_time = time.time()
        
        
            if status == "Normal":
                if pre_status != status:
                    touch_state_history_list.clear()
                    touch_period_history_list.clear()
            
                isValid2Pause = True
                for ai_n in NO_PAUSE_AI_NAME_LIST:
                    if ai_n in miscInfo['status']['name']:
                        isValid2Pause = False
                        break    
     
                if isValid2Pause == True:
                    if len(touch_state_history_list) > 0:
                        if touch_state_history_list[-1] == 1:
                            me.pause()
                            next_status = "NowPause"
                            print(f"# \"extra_bump_behavior\" now status={status}, go to status ={next_status}")
                            

            elif status == "NowPause":
                if len(touch_state_history_list) > 0:
                    if touch_state_history_list[-1] == 1:
                        # Cancel the mission
                        if touch_period_history_list[-1] > 3.0:
                            next_status = "CancelMission"
                            print(f"# \"extra_bump_behavior\" now status={status}, go to status ={next_status}")
                    
                    elif touch_state_history_list[-1] == 0:
                        # Pause a While and Auto Resume
                        if len(touch_state_history_list) >= 2:
                            if touch_state_history_list[-2] == 1:
                                if (touch_period_history_list[-2] <= 3.0):
                                    next_status = "PauseAutoResume"
                                    print(f"# \"extra_bump_behavior\" now status={status}, go to status ={next_status}")



            elif status == "PauseAutoResume":
                if len(touch_state_history_list) > 0:
                    # if touch_state_history_list[-1] == 1:
                        # # Pause but No Auto Resume
                        # if touch_period_history_list[-1] < 10.0:
                            # if len(touch_state_history_list) >= 4:
                                # if (touch_state_history_list[-2] == 0) and \
                                   # (touch_state_history_list[-3] == 1) and \
                                   # (touch_state_history_list[-4] == 0):
                                    
                                    # if (touch_period_history_list[-2] < 10.0) and \
                                       # (touch_period_history_list[-3] < 10.0) and \
                                       # (touch_period_history_list[-4] < 10.0):
                                        # print("# \"extra_bump_behavior\" go to status ={}".format(status))
                                        # next_status = "PauseNoAutoResume"
            
                    if pre_status == status:
                        if touch_period_history_list[-1] > 11.0:
                            me.resume()
                            #touch_state_history_list.clear()
                            #touch_period_history_list.clear()
                            next_status = "Normal"
                            print(f"# \"extra_bump_behavior\" now status={status}, go to status ={next_status}")
        
                
                
            elif status == "CancelMission":
                me.pause()
                touch_state_history_list.clear()
                touch_period_history_list.clear()
                next_status = "Normal"
                print(f"# \"extra_bump_behavior\" now status={status}, go to status ={next_status}")
                
                
            # Push New Data to History list            
            if  miscInfo['ext_io'][0] != pre_touch_state:
                touch_state_history_list.append(miscInfo['ext_io'][0])
                touch_period_history_list.append(time.time() - touch_state_change_start_time)
            
            # Clean the Old History
            if len(touch_state_history_list) > 5:
                touch_state_history_list.pop(0)
            if len(touch_period_history_list) > 5:
                touch_period_history_list.pop(0)
                
            # Update Last History (Now)
            if len(touch_period_history_list) > 0:    
                touch_period_history_list[-1] = time.time() - touch_state_change_start_time
            
            print("# \"extra_bump_behavior\" status ={}".format(status))
            print("# \"extra_bump_behavior\" touch_state_history_list =")
            print(touch_state_history_list)
            print("# \"extra_bump_behavior\" touch_period_history_list =")
            print(touch_period_history_list)
            
            # Update the Previous Touch State Info
            pre_touch_state = miscInfo['ext_io'][0]               

            pre_status = status
            status = next_status
    
        time.sleep(0.1)
    

# Thread for checking whether to open 48V-10A or not
# Thread for custom low battery warning
def cobot_power_behavior():
    isReady = False
    pre_isCobotConnected = False
    cobot_disconnect_start_time = time.time()
    isPowerTurnOn = False
    while(1):
        print("# \"cobot_power_behavior\" processing... ,time={}".format(time.time()))

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
            isCobotConnected = hostPinger.sendPing("192.168.88.7")
            
            print("# \"cobot_power_behavior\" Turn On Power !")
            me.set_internal_misc([0,1,0,0,0,0,0,0],\
                                 [0,1,0,0,0,0,0,0])
            
            if miscInfo['battery']['charging'] == 1:
                if isPowerTurnOn == False:                                         
                    cobot_disconnect_start_time = time.time()
                    isPowerTurnOn = True    

            elif miscInfo['battery']['charging'] == 0:
                if (miscInfo['battery']['power'] < 50) and (miscInfo['battery']['power'] >= 31):
                    mpg123_snd_pid = subprocess.Popen(["mpg123", "/data/etc/extra_ui/battery_below_50_percent_warning.mp3"], shell=False)
                    #mpg123_snd_pid.poll()
                    time.sleep(15.0)

                elif (miscInfo['battery']['power'] < 31) and (miscInfo['battery']['power'] > 0):
                    mpg123_snd_pid = subprocess.Popen(["mpg123", "/data/etc/extra_ui/battery_below_30_percent_warning.mp3"], shell=False)
                    #mpg123_snd_pid.poll()
                    time.sleep(8.0)
            
                if pre_isCobotConnected != isCobotConnected:
                    if isCobotConnected == False:
                        cobot_disconnect_start_time = time.time()
                        
                if isCobotConnected == True:
                    cobot_disconnect_start_time = time.time()
                
                elif isCobotConnected == False:
                    pass

            pre_isCobotConnected = isCobotConnected

        time.sleep(0.3)



    

# Create threads
thread_a = threading.Thread(target = extra_bump_behavior)
# thread_b = threading.Thread(target = cobot_power_behavior)

# Run the thread
thread_a.start()
# thread_b.start()

thread_a.join()
# thread_b.join()

print("End")
