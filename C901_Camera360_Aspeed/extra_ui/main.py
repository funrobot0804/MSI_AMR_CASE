import threading
import time
import os
import subprocess

import device

me = device.robot("127.0.0.1")

hostPinger = device.Pinger()

# Thread for checking whether to open 48V-10A or not
# Thread for custom low battery warning
def camera360_power_behavior():
    isReady = False
    isPowerTurnOn = False
    while(1):
        print("# \"camera360_power_behavior\" processing... ,time={}".format(time.time()))

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
            if isPowerTurnOn == False:
                print("# \"camera360_power_behavior\" Turn On Power !")
                me.set_internal_misc([0,1,0,0,0,0,0,0],\
                                     [0,1,0,0,0,0,0,0])
                isPowerTurnOn = True



        time.sleep(0.3)



    

# Create threads
thread_b = threading.Thread(target = camera360_power_behavior)

# Run the thread
thread_b.start()

thread_b.join()

print("End")
