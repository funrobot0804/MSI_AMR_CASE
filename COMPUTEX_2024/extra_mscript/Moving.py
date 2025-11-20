import device
import time
import os
import sys
import threading

# item_name = ""
# try:
    # item_name = sys.argv[1]
# except:
    # pass

fed_guid = sys.argv[1]

ai_name_prefix = ""

IS_MODBUSTK_INSTALLED = False
try:
    import modbus_tk.modbus_tcp as mt
    import modbus_tk.defines as md
    IS_MODBUSTK_INSTALLED = True
except:
    pass

missioncount = 0

me = device.robot("127.0.0.1")

def SetModbus(ip_addr="",port=502, slave_id=1, reg_or_coil="HOLD_REG", st_addr=0, quantity=1, output_value=1, name="taskindex0" ):
    global missioncount
    missioncount=missioncount+1
    global stepcount
    _timeout=5.0
    
    try:
        if "L" in name:
            stepcount = int(name.split("L")[1])
    except:
        pass

    # missionstarttime=time.time()
    # ainame=scriptName+","+name+",M"+str(missioncount)+",SetModbus("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(output_value)+")"
    # ainame=ainame[0:min(250,len(ainame))]

    # ainame=change_ai_name_by_prefix(ainame,name)
    # ainame=ainame[0:min(250, len(ainame))]

    # origin_ainame = ainame
    # syncprint(scriptName,"SetModbus("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(output_value)+")","start",name,"M"+str(missioncount))

    # write_watch_dog_info("SetModbus 0",ainame)

    # r=get_misc_and_check_basic("SetModbus",name,ainame)
    # if (r["status"]["status"]!=me.STOP)&(r["status"]["status"]!=me.STANDBY):
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName,"error","SetModbus_cannotstart("+aistatus+")",name,"M"+str(missioncount))
        # me.stop("error,SetModbus_cannotstart("+aistatus+"),"+ainame)
        # return Exit()

    # isMoveOutFromDock = False
    # if r['battery']['charging'] == 1:
        # isMoveOutFromDock = True

    # startx=r["position"]["x"]
    # starty=r["position"]["y"]
    # starta=r["position"]["a"]

    # write_watch_dog_info("SetModbus 0", ainame)

    # me.standby(ainame, 1)
    # isAInameSet = ainame_change_checker("SetModbus", name, ainame)
    # if isAInameSet == False:
        # r = get_misc_and_check_basic("SetModbus", name, ainame)
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName, "error", "SetModbus_setainameerror(" + aistatus + ")", name,
                  # "M" + str(missioncount))
        # me.stop("error,SetModbus_setainameerror(" + aistatus + ")," + ainame)
        # return Exit()


    the_modbus_master = None
    if (ip_addr!=""):
        try:
            the_modbus_master = mt.TcpMaster(ip_addr, port)
            the_modbus_master.set_timeout(_timeout)
            the_modbus_master.set_verbose(True)
        except:
            the_modbus_master = None
    else:
        # syncprint(scriptName, "error", "SetModbus_emptyip", name, "M" + str(missioncount))
        # me.stop("error,SetModbus_emptyip," + ainame)
        return -1


    if the_modbus_master is None:
        # syncprint(scriptName, "error", "SetModbus_failedip_or_port", name, "M" + str(missioncount))
        # me.stop("error,SetModbus_failedip_or_port," + ainame)
        return -1

    else:
        try:
            if (reg_or_coil == "HOLD_REG") or (reg_or_coil == "REG"):
                if quantity <= 1:
                    the_modbus_master.execute(slave_id, \
                                              md.WRITE_SINGLE_REGISTER, \
                                              starting_address=st_addr, \
                                              quantity_of_x=quantity, \
                                              output_value=output_value)

                elif quantity > 1:
                    the_modbus_master.execute(slave_id, \
                                              md.WRITE_MULTIPLE_REGISTERS, \
                                              starting_address=st_addr, \
                                              quantity_of_x=quantity, \
                                              output_value=output_value)


            elif reg_or_coil == "COIL":
                if quantity <= 1:
                    bit_val = 0
                    if type(output_value) is list:
                        if len(output_value) > 0:
                            if output_value[0] > 0:
                                bit_val = 1
                            else:
                                bit_val = 0
                        else:
                            bit_val = 0

                    elif type(output_value) is int:
                        if output_value > 0:
                            bit_val = 1
                        else:
                            bit_val = 0


                    the_modbus_master.execute(slave_id, \
                                              md.WRITE_SINGLE_COIL, \
                                              starting_address=st_addr, \
                                              quantity_of_x=1, \
                                              output_value=bit_val)

                elif quantity > 1:
                    for ov in output_value:
                        if ov > 0:
                            ov = 1
                        elif ov <= 0:
                            ov = 0

                    the_modbus_master.execute(slave_id, \
                                              md.WRITE_MULTIPLE_COILS, \
                                              starting_address=st_addr, \
                                              quantity_of_x=quantity, \
                                              output_value=output_value)
                                              
            the_modbus_master = None
            
        except:
            # syncprint(scriptName, "error", "SetModbus_settingvaluefail", name, "M" + str(missioncount))
            the_modbus_master = None
            # me.stop("error,SetModbus_settingvaluefail," + ainame)
            return -1

        return 0
        


def WaitModbusSingleEqual(ip_addr="",port=502, slave_id=1, reg_or_coil="INPUT_REG", st_addr=0, quantity=1,cmp_value=1, name="taskindex0", waittimeout=-1):
    global missioncount
    missioncount=missioncount+1
    global stepcount
    _timeout=5.0
    
    try:
        if "L" in name:
            stepcount = int(name.split("L")[1])
    except:
        pass
        
    # missionstarttime=time.time()
    # ainame=scriptName+","+name+",M"+str(missioncount)+",WaitModbusSingleEqual("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(cmp_value)+")"
    # ainame=ainame[0:min(250,len(ainame))]

    # ainame=change_ai_name_by_prefix(ainame,name)
    # ainame=ainame[0:min(250, len(ainame))]

    # origin_ainame = ainame
    # syncprint(scriptName,"WaitModbusSingleEqual("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(cmp_value)+")","start",name,"M"+str(missioncount))

    # write_watch_dog_info("WaitModbusSingleEqual 0",ainame)

    # r=get_misc_and_check_basic("WaitModbusSingleEqual",name,ainame)
    # if (r["status"]["status"]!=me.STOP)&(r["status"]["status"]!=me.STANDBY):
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName,"error","WaitModbusSingleEqual_cannotstart("+aistatus+")",name,"M"+str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_cannotstart("+aistatus+"),"+ainame)
        # return Exit()

    # isMoveOutFromDock = False
    # if r['battery']['charging'] == 1:
        # isMoveOutFromDock = True

    # startx=r["position"]["x"]
    # starty=r["position"]["y"]
    # starta=r["position"]["a"]

    # write_watch_dog_info("WaitModbusSingleEqual 0", ainame)

    # me.standby(ainame, 1)
    # isAInameSet = ainame_change_checker("WaitModbusSingleEqual", name, ainame)
    # if isAInameSet == False:
        # r = get_misc_and_check_basic("WaitModbusSingleEqual", name, ainame)
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_setainameerror(" + aistatus + ")", name,
                  # "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_setainameerror(" + aistatus + ")," + ainame)
        # return Exit()

    # if IS_MODBUSTK_INSTALLED == False:
        # # me.stop("error,modbustk_notinstalled," + ainame)
        # return -1

    the_modbus_master = None
    if (ip_addr!=""):
        try:
            the_modbus_master = mt.TcpMaster(ip_addr, port)
            the_modbus_master.set_timeout(_timeout)
            the_modbus_master.set_verbose(True)
        except:
            the_modbus_master = None
    else:
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_emptyip", name, "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_emptyip," + ainame)
        return -1


    if the_modbus_master is None:
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_failedip_or_port", name, "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_failedip_or_port," + ainame)
        return -1

    else:
        start_time = time.time()
        for i in range(100000000000):
        
            time.sleep(0.2)

            try:
                if reg_or_coil == "COIL":
                    bit_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_COILS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if bit_val[0] == cmp_value:
                        return 0

                if reg_or_coil == "DISC_INPUT":
                    bit_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_DISCRETE_INPUTS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if bit_val[0] == cmp_value:
                        return 0

                if reg_or_coil == "HOLD_REG":
                    ret_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_HOLDING_REGISTERS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if ret_val[0] == cmp_value:
                        return 0

                if reg_or_coil == "INPUT_REG":
                    ret_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_INPUT_REGISTERS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if ret_val[0] == cmp_value:
                        return 0
                        
                time.sleep(_timeout+0.5)
            except:
                print("# WaitModbusSingleEqual read value fail! time={t}".format(t=time.time()))
                the_modbus_master=None
                time.sleep(_timeout+0.5)
                the_modbus_master=mt.TcpMaster(ip_addr, port)
                the_modbus_master.set_timeout(_timeout)
                the_modbus_master.set_verbose(True)                


            
            if waittimeout >= 0.0:
                if time.time() - start_time > waittimeout:
                    return 0

def WaitModbusSingleEqual_ErrorReturn(ip_addr="",port=502, slave_id=1, reg_or_coil="INPUT_REG", st_addr=0, quantity=1,cmp_value=1, name="taskindex0", waittimeout=-1):
    global missioncount
    missioncount=missioncount+1
    global stepcount
    _timeout=5.0
    
    try:
        if "L" in name:
            stepcount = int(name.split("L")[1])
    except:
        pass
        
    # missionstarttime=time.time()
    # ainame=scriptName+","+name+",M"+str(missioncount)+",WaitModbusSingleEqual("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(cmp_value)+")"
    # ainame=ainame[0:min(250,len(ainame))]

    # ainame=change_ai_name_by_prefix(ainame,name)
    # ainame=ainame[0:min(250, len(ainame))]

    # origin_ainame = ainame
    # syncprint(scriptName,"WaitModbusSingleEqual("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(cmp_value)+")","start",name,"M"+str(missioncount))

    # write_watch_dog_info("WaitModbusSingleEqual 0",ainame)

    # r=get_misc_and_check_basic("WaitModbusSingleEqual",name,ainame)
    # if (r["status"]["status"]!=me.STOP)&(r["status"]["status"]!=me.STANDBY):
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName,"error","WaitModbusSingleEqual_cannotstart("+aistatus+")",name,"M"+str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_cannotstart("+aistatus+"),"+ainame)
        # return Exit()

    # isMoveOutFromDock = False
    # if r['battery']['charging'] == 1:
        # isMoveOutFromDock = True

    # startx=r["position"]["x"]
    # starty=r["position"]["y"]
    # starta=r["position"]["a"]

    # write_watch_dog_info("WaitModbusSingleEqual 0", ainame)

    # me.standby(ainame, 1)
    # isAInameSet = ainame_change_checker("WaitModbusSingleEqual", name, ainame)
    # if isAInameSet == False:
        # r = get_misc_and_check_basic("WaitModbusSingleEqual", name, ainame)
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_setainameerror(" + aistatus + ")", name,
                  # "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_setainameerror(" + aistatus + ")," + ainame)
        # return Exit()

    # if IS_MODBUSTK_INSTALLED == False:
        # # me.stop("error,modbustk_notinstalled," + ainame)
        # return -1

    the_modbus_master = None
    if (ip_addr!=""):
        try:
            the_modbus_master = mt.TcpMaster(ip_addr, port)
            the_modbus_master.set_timeout(_timeout)
            the_modbus_master.set_verbose(True)
        except:
            the_modbus_master = None
    else:
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_emptyip", name, "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_emptyip," + ainame)
        return -1


    if the_modbus_master is None:
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_failedip_or_port", name, "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_failedip_or_port," + ainame)
        return -1

    else:
        start_time = time.time()
        for i in range(100000000000):
        
            time.sleep(0.2)

            try:
                if reg_or_coil == "COIL":
                    bit_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_COILS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if bit_val[0] == cmp_value:
                        return 0
                    else:
                        return -1

                if reg_or_coil == "DISC_INPUT":
                    bit_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_DISCRETE_INPUTS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if bit_val[0] == cmp_value:
                        return 0
                    else:
                        return -1

                if reg_or_coil == "HOLD_REG":
                    ret_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_HOLDING_REGISTERS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if ret_val[0] == cmp_value:
                        return 0
                    else:
                        return -1

                if reg_or_coil == "INPUT_REG":
                    ret_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_INPUT_REGISTERS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if ret_val[0] == cmp_value:
                        return 0
                    else:
                        return -1
                        
                time.sleep(_timeout+0.5)
            except:
                print("# WaitModbusSingleEqual_ErrorReturn read value fail! time={t}".format(t=time.time()))
                the_modbus_master=None
                time.sleep(_timeout+0.5)
                the_modbus_master=mt.TcpMaster(ip_addr, port)
                the_modbus_master.set_timeout(_timeout)
                the_modbus_master.set_verbose(True)                


            
            if waittimeout >= 0.0:
                if time.time() - start_time > waittimeout:
                    return -1


def CheckTMCobotSafetyStatus(ip_addr="",port=502, slave_id=1, reg_or_coil="DISC_INPUT", st_addr=7201, quantity=4, cmp_value=1, name="taskindex0", waittimeout=-1):
    global missioncount
    missioncount=missioncount+1
    global stepcount
    _timeout=5.0
    
    try:
        if "L" in name:
            stepcount = int(name.split("L")[1])
    except:
        pass
        
    # missionstarttime=time.time()
    # ainame=scriptName+","+name+",M"+str(missioncount)+",WaitModbusSingleEqual("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(cmp_value)+")"
    # ainame=ainame[0:min(250,len(ainame))]

    # ainame=change_ai_name_by_prefix(ainame,name)
    # ainame=ainame[0:min(250, len(ainame))]

    # origin_ainame = ainame
    # syncprint(scriptName,"WaitModbusSingleEqual("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(cmp_value)+")","start",name,"M"+str(missioncount))

    # write_watch_dog_info("WaitModbusSingleEqual 0",ainame)

    # r=get_misc_and_check_basic("WaitModbusSingleEqual",name,ainame)
    # if (r["status"]["status"]!=me.STOP)&(r["status"]["status"]!=me.STANDBY):
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName,"error","WaitModbusSingleEqual_cannotstart("+aistatus+")",name,"M"+str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_cannotstart("+aistatus+"),"+ainame)
        # return Exit()

    # isMoveOutFromDock = False
    # if r['battery']['charging'] == 1:
        # isMoveOutFromDock = True

    # startx=r["position"]["x"]
    # starty=r["position"]["y"]
    # starta=r["position"]["a"]

    # write_watch_dog_info("WaitModbusSingleEqual 0", ainame)

    # me.standby(ainame, 1)
    # isAInameSet = ainame_change_checker("WaitModbusSingleEqual", name, ainame)
    # if isAInameSet == False:
        # r = get_misc_and_check_basic("WaitModbusSingleEqual", name, ainame)
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_setainameerror(" + aistatus + ")", name,
                  # "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_setainameerror(" + aistatus + ")," + ainame)
        # return Exit()

    # if IS_MODBUSTK_INSTALLED == False:
        # # me.stop("error,modbustk_notinstalled," + ainame)
        # return -1

    the_modbus_master = None
    if (ip_addr!=""):
        try:
            the_modbus_master = mt.TcpMaster(ip_addr, port)
            the_modbus_master.set_timeout(_timeout)
            the_modbus_master.set_verbose(True)
        except:
            the_modbus_master = None
    else:
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_emptyip", name, "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_emptyip," + ainame)
        return -1


    if the_modbus_master is None:
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_failedip_or_port", name, "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_failedip_or_port," + ainame)
        return -1

    else:
        start_time = time.time()
        for i in range(100000000000):
        
            time.sleep(0.2)

            try:
                if reg_or_coil == "COIL":
                    bit_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_COILS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if bit_val[0] == cmp_value:
                        return 0
                    else:
                        return -1

                if reg_or_coil == "DISC_INPUT":
                    
                    bit_val = [-1, -1, -1, -1]
                    estop_val = [-1]
                    
                    bit_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_DISCRETE_INPUTS, \
                                                        starting_address=7201, \
                                                        quantity_of_x=4)
                    
                    estop_val = the_modbus_master.execute(slave_id, \
                                    md.READ_DISCRETE_INPUTS, \
                                    starting_address=7208, \
                                    quantity_of_x=1)
                                    
                    the_modbus_master = None
                    
                    return bit_val[0], bit_val[3], estop_val[0]




                if reg_or_coil == "HOLD_REG":
                    ret_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_HOLDING_REGISTERS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if ret_val[0] == cmp_value:
                        return 0
                    else:
                        return -1

                if reg_or_coil == "INPUT_REG":
                    ret_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_INPUT_REGISTERS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if ret_val[0] == cmp_value:
                        return 0
                    else:
                        return -1
                        
                time.sleep(_timeout+0.5)
            except:
                print("# CheckTMCobotSafetyStatus read value fail! time={t}".format(t=time.time()))
                the_modbus_master=None
                time.sleep(_timeout+0.5)
                the_modbus_master=mt.TcpMaster(ip_addr, port)
                the_modbus_master.set_timeout(_timeout)
                the_modbus_master.set_verbose(True)                


            
            if waittimeout >= 0.0:
                if time.time() - start_time > waittimeout:
                    return -1
                    


def CheckTMCobotButtonPressed(ip_addr="",port=502, slave_id=1, reg_or_coil="DISC_INPUT", st_addr=7153, quantity=1, cmp_value=1, name="taskindex0", waittimeout=-1):
    global missioncount
    missioncount=missioncount+1
    global stepcount
    _timeout=5.0
    
    try:
        if "L" in name:
            stepcount = int(name.split("L")[1])
    except:
        pass
        
    # missionstarttime=time.time()
    # ainame=scriptName+","+name+",M"+str(missioncount)+",WaitModbusSingleEqual("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(cmp_value)+")"
    # ainame=ainame[0:min(250,len(ainame))]

    # ainame=change_ai_name_by_prefix(ainame,name)
    # ainame=ainame[0:min(250, len(ainame))]

    # origin_ainame = ainame
    # syncprint(scriptName,"WaitModbusSingleEqual("+str(ip_addr)+";"+str(port)+";"+str(slave_id)+";"+str(st_addr)+";"+str(quantity)+";"+str(cmp_value)+")","start",name,"M"+str(missioncount))

    # write_watch_dog_info("WaitModbusSingleEqual 0",ainame)

    # r=get_misc_and_check_basic("WaitModbusSingleEqual",name,ainame)
    # if (r["status"]["status"]!=me.STOP)&(r["status"]["status"]!=me.STANDBY):
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName,"error","WaitModbusSingleEqual_cannotstart("+aistatus+")",name,"M"+str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_cannotstart("+aistatus+"),"+ainame)
        # return Exit()

    # isMoveOutFromDock = False
    # if r['battery']['charging'] == 1:
        # isMoveOutFromDock = True

    # startx=r["position"]["x"]
    # starty=r["position"]["y"]
    # starta=r["position"]["a"]

    # write_watch_dog_info("WaitModbusSingleEqual 0", ainame)

    # me.standby(ainame, 1)
    # isAInameSet = ainame_change_checker("WaitModbusSingleEqual", name, ainame)
    # if isAInameSet == False:
        # r = get_misc_and_check_basic("WaitModbusSingleEqual", name, ainame)
        # aistatus = fix_ai_status_string(r["status"])
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_setainameerror(" + aistatus + ")", name,
                  # "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_setainameerror(" + aistatus + ")," + ainame)
        # return Exit()

    # if IS_MODBUSTK_INSTALLED == False:
        # # me.stop("error,modbustk_notinstalled," + ainame)
        # return -1

    the_modbus_master = None
    if (ip_addr!=""):
        try:
            the_modbus_master = mt.TcpMaster(ip_addr, port)
            the_modbus_master.set_timeout(_timeout)
            the_modbus_master.set_verbose(True)
        except:
            the_modbus_master = None
    else:
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_emptyip", name, "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_emptyip," + ainame)
        return -1


    if the_modbus_master is None:
        # syncprint(scriptName, "error", "WaitModbusSingleEqual_failedip_or_port", name, "M" + str(missioncount))
        # me.stop("error,WaitModbusSingleEqual_failedip_or_port," + ainame)
        return -1

    else:
        start_time = time.time()
        for i in range(100000000000):
        
            time.sleep(0.2)

            try:
                if reg_or_coil == "COIL":
                    bit_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_COILS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if bit_val[0] == cmp_value:
                        return 0
                    else:
                        return -1

                if reg_or_coil == "DISC_INPUT":
                    
                    bit_val = [-1]
                    
                    bit_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_DISCRETE_INPUTS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                                    
                    the_modbus_master = None
                    
                    return bit_val[0]



                if reg_or_coil == "HOLD_REG":
                    ret_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_HOLDING_REGISTERS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if ret_val[0] == cmp_value:
                        return 0
                    else:
                        return -1

                if reg_or_coil == "INPUT_REG":
                    ret_val = the_modbus_master.execute(slave_id, \
                                                        md.READ_INPUT_REGISTERS, \
                                                        starting_address=st_addr, \
                                                        quantity_of_x=1)
                    the_modbus_master = None
                    if ret_val[0] == cmp_value:
                        return 0
                    else:
                        return -1
                        
                time.sleep(_timeout+0.5)
            except:
                print("# CheckTMCobotSafetyStatus read value fail! time={t}".format(t=time.time()))
                the_modbus_master=None
                time.sleep(_timeout+0.5)
                the_modbus_master=mt.TcpMaster(ip_addr, port)
                the_modbus_master.set_timeout(_timeout)
                the_modbus_master.set_verbose(True)                


            
            if waittimeout >= 0.0:
                if time.time() - start_time > waittimeout:
                    return -1                    
                    
                    
                    


isButtonClicked = False
def StopButtonChecking():
    isEnd = False
    while(isEnd==False):
        isStopBtnPressed = CheckTMCobotButtonPressed(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="DISC_INPUT", st_addr=7153)

        print("# StopButtonChecking, time=", time.time())
        print("# StopButtonChecking, isStopBtnPressed =", isStopBtnPressed)

        if isStopBtnPressed == 1:
            isEnd = True
            print(f"Moving, {fed_guid}, Stop, Error")

            now_ai_name = ai_name_prefix + str(fed_guid) + ",Error"
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
                
            os._exit(1)

        time.sleep(0.2)
        

def PauseButtonChecking():
    isEnd = False
    while(isEnd==False):
        isBtnPressed = CheckTMCobotButtonPressed(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="DISC_INPUT", st_addr=7152)

        print("# PauseButtonChecking, time=", time.time())
        print("# PauseButtonChecking, isBtnPressed =", isBtnPressed)

        if isBtnPressed == 1:
            isEnd = True
            print(f"Moving, {fed_guid}, Pause, Error")

            now_ai_name = ai_name_prefix + str(fed_guid) + ",Error"
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
                
            os._exit(1)

        time.sleep(0.2)
        

def MAButtonChecking():
    isEnd = False
    while(isEnd==False):
        isBtnPressed = CheckTMCobotButtonPressed(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="DISC_INPUT", st_addr=7151)

        print("# MAButtonChecking, time=", time.time())
        print("# MAButtonChecking, isBtnPressed =", isBtnPressed)

        if isBtnPressed == 1:
            isEnd = True
            print(f"Moving, {fed_guid}, MAButton, Error")

            now_ai_name = ai_name_prefix + str(fed_guid) + ",Error"
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
                
            os._exit(1)

        time.sleep(0.2)  

def MAModeChecking():
    isEnd = False
    while(isEnd==False):
        isBtnPressed = CheckTMCobotButtonPressed(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="INPUT_REG", st_addr=7102)
        
        print("# MAModeChecking, time=", time.time())
        print("# MAModeChecking, isBtnPressed =", isBtnPressed)

        if isBtnPressed == -1:
            isEnd = True
            print(f"Moving, {fed_guid}, MAMode, Error")

            now_ai_name = ai_name_prefix + str(fed_guid) + ",Error"
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
                
            os._exit(1)

        time.sleep(0.2)         
        



                    

new_thread_1 = threading.Thread(target = StopButtonChecking)          
new_thread_1.start()

new_thread_2 = threading.Thread(target = PauseButtonChecking)          
new_thread_2.start()  

new_thread_3 = threading.Thread(target = MAButtonChecking)          
new_thread_3.start()

new_thread_4 = threading.Thread(target = MAModeChecking)          
new_thread_4.start()                   
                    
                    
                    
                    


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

input = "80"
input_hex_str_list = [ item.encode('utf-8').hex() for item in input ]
final_hex_string = "0x"
for the_str in input_hex_str_list:
    final_hex_string += the_str
    
an_integer = int(final_hex_string, 16)
hex_value = hex(an_integer)

print("# an_integer =", an_integer)

SetModbus(ip_addr="192.168.88.7", port=502, slave_id=1, reg_or_coil="HOLD_REG", \
          st_addr=7701, quantity=1, output_value=an_integer, name="taskindex0")

WaitModbusSingleEqual(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="INPUT_REG", \
                      st_addr=7701, quantity=1, cmp_value=an_integer, name="taskindex0", waittimeout=-1)

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


          
SetModbus(ip_addr="192.168.88.7", port=502, slave_id=1, reg_or_coil="COIL", \
          st_addr=7104, quantity=1, output_value=1, name="taskindex0")
          
time.sleep(5.0)          

WaitModbusSingleEqual(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="DISC_INPUT", \
                      st_addr=7202, quantity=1, cmp_value=0, name="taskindex0", waittimeout=-1)
                      
isCobotError = -1
isCobotPause = -1
isCobotEstop = -1
isStopBtnPressed = -1

# isCobotError = WaitModbusSingleEqual_ErrorReturn(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="DISC_INPUT", \
                      # st_addr=7201, quantity=1, cmp_value=0, name="taskindex0", waittimeout=-1)
                      
# isCobotPause = WaitModbusSingleEqual_ErrorReturn(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="DISC_INPUT", \
                      # st_addr=7204, quantity=1, cmp_value=0, name="taskindex0", waittimeout=-1)                      

# isCobotEstop = WaitModbusSingleEqual_ErrorReturn(ip_addr="192.168.88.7",port=502, slave_id=1, reg_or_coil="DISC_INPUT", \
                      # st_addr=7208, quantity=1, cmp_value=0, name="taskindex0", waittimeout=-1)


isCobotError, isCobotPause, isCobotEstop = CheckTMCobotSafetyStatus(ip_addr="192.168.88.7",port=502, slave_id=1)
isStopBtnPressed = CheckTMCobotButtonPressed(ip_addr="192.168.88.7",port=502, slave_id=1)                     


# ===================================

if (isStopBtnPressed==1):
    print(f"Moving, {fed_guid}, Stop Btn Pressed, Error")

    now_ai_name = ai_name_prefix + str(fed_guid) + ",Error"
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

if (isCobotPause==1):
    print(f"Moving, {fed_guid}, Pause Btn Pressed, Error")

    now_ai_name = ai_name_prefix + str(fed_guid) + ",Error"
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
        
    os._exit(1)    


if (isCobotError==0) and (isCobotPause==0) and (isCobotEstop==0):
    print(f"Moving, {fed_guid}, End")

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
        
else:
    print(f"Moving, {fed_guid}, Other Error, Error")

    now_ai_name = ai_name_prefix + str(fed_guid) + ",Error"
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

os._exit(1)

