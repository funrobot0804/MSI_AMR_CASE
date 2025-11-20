import sys
import time

import serial
import argparse
import threading

#add logging capability
import logging

import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
import time
from datetime import datetime


class PlcRollerRs485():
    def __init__(self):
        self.logger = modbus_tk.utils.create_logger("console")

        self.master = None

        self.req_state = "STANDBY" # "AUTO_MODE_ON", "SET_SLOT"
        self.ack_signal = 0
        self.req_data = []
        self.isFinish = 1

        self.current_slot_num = 1
        self.start_time = time.time()

        self.start_live_time = time.time()
        self.start_live_status = 0
        self.reset_err_start_time = time.time()

        self.normal_info = []

    def InitRs485(self):
        self.master = modbus_rtu.RtuMaster(serial.Serial(port="/dev/ttyS2", \
                                                         baudrate=9600, \
                                                         bytesize=8, \
                                                         parity='N', \
                                                         stopbits=1, \
                                                         xonxoff=0))
        self.master.set_timeout(5.0)
        self.master.set_verbose(True)

    def ResetReqState(self):
        self.req_state = "STANDBY"
        self.isFinish = 1

    def SetReqState(self, req_state=""):
        self.req_state = req_state
        self.isFinish = 0

    def SetReqData(self, req_data=[]):
        self.req_data = req_data

    def SetAck(self, ack_signal=0):
        self.ack_signal = ack_signal

    def single_process(self):

        if time.time() - self.start_live_time >= 2.0:
            if self.start_live_status == 0:
                print("PlcRollerRs485 - single_process - breathe ON")
                result = self.master.execute(1, 5, 0x7854, output_value=1)
                self.start_live_status = 1

            elif self.start_live_status == 1:
                print("PlcRollerRs485 - single_process - Normal Ask Info")
                self.normal_info = self.master.execute(1, 1, 0x7810, 20)
                self.start_live_status = 2

            elif self.start_live_status == 2:
                print("PlcRollerRs485 - single_process - breathe OFF")
                result = self.master.execute(1, 5, 0x7854, output_value=0)
                self.start_live_status = 0

            self.start_live_time = time.time()


        result = None

        if self.req_state == "SLOT_1_REQ_OFF":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                self.start_time = time.time()

                reg_addr = 0x7860
                print(f"PlcRollerRs485 - single_process - SLOT_1_REQ_OFF - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=0)
                
                time.sleep(0.2)
                
                reg_addr = 0x7861
                print(f"PlcRollerRs485 - single_process - SLOT_2_REQ_OFF - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=0)
                
                time.sleep(0.2)
                
                reg_addr = 0x7862
                print(f"PlcRollerRs485 - single_process - SLOT_3_REQ_OFF - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=0)

                time.sleep(0.2)

                self.ack_signal = 0
                self.isFinish = 1



        if self.req_state == "AUTO_MODE_ON":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7850
                print(f"PlcRollerRs485 - single_process - AUTO_MODE_ON - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=1)
                self.ack_signal = 0
                self.isFinish = 1



        if self.req_state == "AUTO_MODE_OPERATION_REQ":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7870
                print(f"PlcRollerRs485 - single_process - AUTO_MODE_OPERATION_REQ - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=1)
                self.req_state = "WAIT_AUTO_MODE_OPERATION_REQ"

        if self.req_state == "WAIT_AUTO_MODE_OPERATION_REQ":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7820
                print(f"PlcRollerRs485 - single_process - WAIT_AUTO_MODE_OPERATION_REQ - addr:{reg_addr}")
                result = self.master.execute(1, 1, reg_addr, 1)
                if result[0] == 1:
                    self.ack_signal = 0
                    self.isFinish = 1



        if self.req_state == "INITIALIZE_MODE_ON":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7852
                print(f"PlcRollerRs485 - single_process - INITIALIZE_MODE_ON - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=1)
                self.ack_signal = 0
                self.isFinish = 1



        if self.req_state == "INITIALIZE_MODE_OFF":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7852
                print(f"PlcRollerRs485 - single_process - INITIALIZE_MODE_OFF - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=0)
                self.ack_signal = 0
                self.isFinish = 1




        if self.req_state == "INITIALIZE_OPERATION_REQ":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7872
                print(f"PlcRollerRs485 - single_process - INITIALIZE_OPERATION_REQ - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=1)
                self.req_state = "WAIT_INITIALIZE_OPERATION_DONE"



        if self.req_state == "WAIT_INITIALIZE_OPERATION_DONE":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7822
                print(f"PlcRollerRs485 - single_process - WAIT_INITIALIZE_OPERATION_DONE - addr:{reg_addr}")
                result = self.master.execute(1, 1, reg_addr, 1)
                if result[0] == 1:
                    self.ack_signal = 0
                    self.isFinish = 1



        if self.req_state == "INITIALIZE_OPERATION_REQ_OFF":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7872
                print(f"PlcRollerRs485 - single_process - INITIALIZE_OPERATION_REQ_OFF - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=0)
                self.req_state = "WAIT_INITIALIZE_OPERATION_REQ_OFF"

        if self.req_state == "WAIT_INITIALIZE_OPERATION_REQ_OFF":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7822
                print(f"PlcRollerRs485 - single_process - WAIT_INITIALIZE_OPERATION_REQ_OFF - addr:{reg_addr}")
                result = self.master.execute(1, 1, reg_addr, 1)
                if result[0] == 0:
                    self.ack_signal = 0
                    self.isFinish = 1



        if self.req_state == "SET_SLOT":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                slot_num = self.req_data[0]
                self.current_slot_num = slot_num

                reg_addr = 0x000A
                print(f"PlcRollerRs485 - single_process - SET_SLOT - addr:{reg_addr}, val:{self.current_slot_num}")
                result = self.master.execute(1, 6, reg_addr, output_value=self.current_slot_num)

                self.ack_signal = 0
                self.isFinish = 1


        if self.req_state == "SET_SLOT_ACT":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                slot_act = 0
                if self.req_data[0] == "Get":
                    slot_act = 1
                elif self.req_data[0] == "Put":
                    slot_act = 2

                print("self.req_data[0] =", self.req_data[0])

                reg_addr = 0x000B
                print(f"PlcRollerRs485 - single_process - SET_SLOT_ACT - addr:{reg_addr}, val:{slot_act}")
                result = self.master.execute(1, 6, reg_addr, output_value=slot_act)

                self.ack_signal = 0
                self.isFinish = 1


        if self.req_state == "DO_ACT":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                self.start_time = time.time()

                if self.current_slot_num == 1:
                    reg_addr = 0x7860
                elif self.current_slot_num == 2:
                    reg_addr = 0x7861    
                elif self.current_slot_num == 3:
                    reg_addr = 0x7862
                
                
                print(f"PlcRollerRs485 - single_process - DO_ACT - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=1)

                time.sleep(1.0)
                self.req_state = "FINISH_ACT"



        if self.req_state == "FINISH_ACT":
            complete_address = 0x7810
            result = self.master.execute(1, 1, complete_address, 20)

            busy_idx = 0
            complete_idx = 3
            fail_idx = 6

            if self.current_slot_num == 1:
                complete_idx = complete_idx + 0
                fail_idx = fail_idx + 0
                busy_idx = busy_idx + 0
            elif self.current_slot_num == 2:
                complete_idx = complete_idx + 1
                fail_idx = fail_idx + 1
                busy_idx = busy_idx + 1
            elif self.current_slot_num == 3:
                complete_idx = complete_idx + 2
                fail_idx = fail_idx + 2
                busy_idx = busy_idx + 2


            print(f"PlcRollerRs485 - single_process - FINISH_ACT - addr:{complete_address}")
            print(f"PlcRollerRs485 - single_process - FINISH_ACT - result check = {result}")

            if self.current_slot_num == 1:
                reg_addr = 0x7860
            elif self.current_slot_num == 2:
                reg_addr = 0x7861    
            elif self.current_slot_num == 3:
                reg_addr = 0x7862


            if result[busy_idx] == 0:
                if result[complete_idx] == 1:
                    result = self.master.execute(1, 5, reg_addr, output_value=0)
                    self.req_state = "STANDBY"
                    self.ack_signal = 0
                    self.isFinish = 1


                elif result[fail_idx] == 1:
                    result = self.master.execute(1, 5, reg_addr, output_value=0)
                    self.req_state = "ERROR"
                    self.ack_signal = 0
                    self.isFinish = 1


            if result[-1] == 1:
                result = self.master.execute(1, 5, reg_addr, output_value=0)
                self.req_state = "ERROR"
                self.ack_signal = 0
                self.isFinish = 1


        if self.req_state == "RESET_ERROR":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x7873
                print(f"PlcRollerRs485 - single_process - RESET_ERROR - addr:{reg_addr}")
                result = self.master.execute(1, 5, reg_addr, output_value=1)

                if len(self.normal_info) > 0:
                    if self.normal_info[-1] == 1:
                        self.req_state = "RESET_ERROR_DUMP_RP"
                        self.reset_err_start_time = time.time()
                    else:
                        self.req_state = "RESET_ERROR_OFF"
                        self.reset_err_start_time = time.time()    

        if self.req_state == "RESET_ERROR_DUMP_RP":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:
                reg_addr = 0x30
                print(f"PlcRollerRs485 - single_process - RESET_ERROR_DUMP_RP - addr:{reg_addr}")
                result = self.master.execute(1, 3, reg_addr, 5)

                hex_yymm = result[0]
                hex_ddhh = result[1]
                hex_mmss = result[2]
                int_code = result[3]
                handled = result[4]

                now = datetime.now()  # current date and time
                date_time = now.strftime("%Y-%m-%d-%H-%M-%S")
                log_fn = "/data/dump/PlcRollerRs485_Log_" + date_time + ".txt"
                f = open(log_fn, "w")

                log_str = ""
                log_str += "%X" % hex_yymm + "\n"
                log_str += "%X" % hex_ddhh + "\n"
                log_str += "%X" % hex_mmss + "\n"
                log_str += "%X" % int_code + "\n"
                log_str += "%X" % handled + "\n"

                f.write(log_str)
                f.close()


                self.req_state = "RESET_ERROR_OFF"
                self.reset_err_start_time = time.time()
                
                # self.req_state = "STANDBY"
                # self.ack_signal = 0
                # self.isFinish = 1


        if self.req_state == "RESET_ERROR_OFF":
            if self.ack_signal == 0:
                pass

            elif self.ack_signal == 1:

                if time.time() - self.reset_err_start_time > 1.0:
                    reg_addr = 0x7873
                    print(f"PlcRollerRs485 - single_process - RESET_ERROR_OFF - addr:{reg_addr}")
                    result = self.master.execute(1, 5, reg_addr, output_value=0)
                    self.req_state = "STANDBY"
                    self.ack_signal = 0
                    self.isFinish = 1




        if result is not None:
            print(f"PlcRollerRs485 - single_process - result = {result}")




if __name__ == "__main__":

    prr = PlcRollerRs485()
    prr.InitRs485()

    breathe_time = time.time()
    breathe_status = 0

    def Breathe():
        prr.single_process()


    thread_a = threading.Thread(target=Breathe)
    thread_a.start()


    menu_str = '''
    ===== MENU =====
    1.  AUTO_MODE_ON
    2.  SET_SLOT
    3.  SET_SLOT_ACT
    4.  DO_ACT
    5.  RESET_ERROR
    ...
    6.  INITIALIZE_MODE_ON
    7.  INITIALIZE_OPERATION_REQ
    8.  AUTO_MODE_OPERATION_REQ
    9.  INITIALIZE_MODE_OFF
    10. INITIALIZE_OPERATION_REQ_OFF
    ================
    '''

    slot_act_str = '''
    ===== SLOT ACT =====
    1. Get
    2. Put
    ====================
    '''

    while(1):

        print(f"PlcRollerRs485 - state: {prr.req_state}, isFinish: {prr.isFinish}")

        if prr.isFinish == 1:
            print(menu_str)
            input_opt = input("Choose Testing Option: ")
            input_opt = int(input_opt)

            if input_opt == 1:
                prr.SetReqState("AUTO_MODE_ON")
                prr.SetAck(1)
                pass


            if input_opt == 2:
                slot_num = input("Choose Slot Number: ")
                prr.SetReqState("SET_SLOT")
                slot_num = int(slot_num)
                prr.SetReqData([slot_num])
                prr.SetAck(1)
                pass


            if input_opt == 3:
                print(slot_act_str)
                num = input("Choose Slot Act: ")
                act_str = "Get"
                if num == str(1):
                    act_str = "Get"
                elif num == str(2):
                    act_str = "Put"

                prr.SetReqState("SET_SLOT_ACT")
                prr.SetReqData([act_str])
                prr.SetAck(1)
                pass


            if input_opt == 4:
                prr.SetReqState("DO_ACT")
                prr.SetAck(1)
                pass


            if input_opt == 5:
                prr.SetReqState("RESET_ERROR")
                prr.SetAck(1)
                pass

            if input_opt == 6:
                prr.SetReqState("INITIALIZE_MODE_ON")
                prr.SetAck(1)
                pass

            if input_opt == 7:
                prr.SetReqState("INITIALIZE_OPERATION_REQ")
                prr.SetAck(1)
                pass

            if input_opt == 8:
                prr.SetReqState("AUTO_MODE_OPERATION_REQ")
                prr.SetAck(1)
                pass

            if input_opt == 9:
                prr.SetReqState("INITIALIZE_MODE_OFF")
                prr.SetAck(1)
                pass
                
            if input_opt == 10:
                prr.SetReqState("INITIALIZE_OPERATION_REQ_OFF")
                prr.SetAck(1)
                pass

        time.sleep(0.2)









