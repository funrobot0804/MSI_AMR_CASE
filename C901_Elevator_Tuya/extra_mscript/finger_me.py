'''
example (click): 
python3 finger_me.py -c finger1.json; echo $?

example (switch on): 
python3 finger_me.py -c finger1.json -sw 1; echo $?

example (switch off): 
python3 finger_me.py -c finger1.json -sw 0; echo $?
'''
from pyfingerbot import FingerBot
import logging
import json
import signal
import argparse
import sys
import time
import os



log = logging.getLogger(__name__)
disable_BLE_flag="/tmp/beacon_disable"
###################################################################################################
def touch(file_path):
    if os.path.exists(file_path)==False:    
        with open(file_path, 'a'):
            os.utime(file_path, None)
###################################################################################################
if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')
    #logging.getLogger('pygatt').setLevel(logging.DEBUG)

        
    # Initiate the parser
    parser = argparse.ArgumentParser()
    
    # Add long and short argument
    parser.add_argument("--configure", "-c", type=str, default="finger1.json", help="key file from tuya")
    parser.add_argument("--switch_on_off", "-sw", type=int, default=-1, help="1:on 0:off configure have to setup as switch mode first")
    parser.add_argument("--test_value", "-tv", type=int, default=-1, help="input test value")

    # Read arguments from the command line
    args = parser.parse_args()    
    
    
    log.info("Load config %s" % (args.configure))
    
    # Opening JSON file
    f = open(args.configure)
    
    # returns JSON object as 
    # a dictionary
    jdata = json.load(f)
    f.close()
    
    
    # Use https://github.com/redphx/tuya-local-key-extractor to get these values
    LOCAL_KEY = jdata['certificate']['local_key']
    MAC = jdata['certificate']['mac_address']
    UUID = jdata['certificate']['uuid']
    DEV_ID = jdata['certificate']['device_id']
    
    mode=0
    if args.switch_on_off==-1:
        mode=0 #0:click 1:switch
    else:
        mode=1
        
    #print("switch_on_off=%d mode=%d" % (args.switch_on_off,mode))
    fingerbot = FingerBot(jdata['certificate']['mac_address'], 
                          jdata['certificate']['local_key'], 
                          jdata['certificate']['uuid'], 
                          jdata['certificate']['device_id'],
                          jdata['certificate']['product_id'],
                          jdata['fingerbot']['hci_device'],
                          mode,
                          args.switch_on_off,
                          args.test_value)
    
    #stop BLE beacon
    log.info("Stop BLE beacon")
    touch(disable_BLE_flag)
    time.sleep(0.5)
    
    start=time.time()
    error=0
    while(True):
        if fingerbot.connect(5)==True:
            fingerbot.finger()
            break
        else:
            if (time.time()-start)>jdata['fingerbot']['connection_timeout']:
                log.warning("Failure %s" % (args.configure))
                error=1
                break
            else:
                fingerbot.disconnect()


    fingerbot.disconnect()
    
    #start BLE beacon
    log.info("Start BLE beacon")
    os.remove(disable_BLE_flag)
        
    if error==1:
        sys.exit(-1)
    else:
        sys.exit(0)