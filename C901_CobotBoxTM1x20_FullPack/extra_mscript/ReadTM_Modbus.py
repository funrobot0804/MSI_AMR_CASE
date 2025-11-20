#!/usr/bin/env python
# -*- coding: utf_8 -*-
"""
 Modbus TestKit: Implementation of Modbus protocol in python

 (C)2009 - Luc Jean - luc.jean@gmail.com
 (C)2009 - Apidev - http://www.apidev.fr

 This is distributed under GNU LGPL license, see license.txt
"""

import sys
import serial
import argparse

#add logging capability
import logging

import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
import modbus_tk.modbus_tcp as mt
#import modbus_tk.defines as md

logger = modbus_tk.utils.create_logger("console")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-t","--type",type=int)
    parser.add_argument("-a","--address",type=str)
    parser.add_argument("-q","--quantity",type=int)
    args = parser.parse_args()
    
    print("args.type =", args.type)
    print("args.quantity =", args.quantity)
    
    print("args.address =", args.address)
    hex_address = "0x" + args.address
    int_address = int(hex_address, 16)
    print("int(args.address) =", int_address)
    print("hex(int(args.address)) =", hex(int_address))
    
    
    try:
        #Connect to the slave
        master = mt.TcpMaster("192.168.88.7", 502)
        master.set_timeout(120.0)
        master.set_verbose(True)
        print("connected")
        logger.info("connected")
        
        #logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 100, 3))
        
        #send some queries
        #logger.info(master.execute(1, cst.READ_COILS, 0, 10))
        #logger.info(master.execute(1, cst.READ_DISCRETE_INPUTS, 0, 8))
        #logger.info(master.execute(1, cst.READ_INPUT_REGISTERS, 100, 3))
        #logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 100, 12))
        #logger.info(master.execute(1, cst.WRITE_SINGLE_COIL, 7, output_value=1))
        #logger.info(master.execute(1, cst.WRITE_SINGLE_REGISTER, 100, output_value=54))
        #logger.info(master.execute(1, cst.WRITE_MULTIPLE_COILS, 0, output_value=[1, 1, 0, 1, 1, 0, 1, 1]))
        #logger.info(master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 100, output_value=xrange(12)))
        
        
        result = master.execute(1, args.type, int_address, args.quantity)

        print("result =", result)
        print("HEX result =")
        for rr in result:
            print("%X "%rr)
        print("")
        
        pass
        
    except modbus_tk.modbus.ModbusError as e:
        print("%s- Code=%d" % (e, e.get_exception_code()))
        
        
        
        
        