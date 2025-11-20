'''
reference:
https://github.com/PlusPlus-ua/ha_tuya_ble/blob/main/custom_components/tuya_ble/tuya_ble/const.py
https://solution.tuya.com/cn/projects/CMawjdxoylsgnm
file:///C:/Users/lkklk/Downloads/%E8%93%9D%E7%89%99%E9%97%A8%E9%94%81%E5%B0%8F%E7%A8%8B%E5%BA%8F%20SDK_%E6%B6%82%E9%B8%A6%E6%99%BA%E8%83%BD_%E6%96%87%E6%A1%A3%E4%B8%AD%E5%BF%83.pdf
'''
import time
import pygatt
import hashlib
import secrets
from Crypto.Cipher import AES
from struct import pack, unpack
from enum import Enum
from binascii import hexlify
import logging

import binascii



log = logging.getLogger(__name__)
###################################################################################################
class Coder(Enum):
    FUN_SENDER_DEVICE_INFO = 0
    FUN_SENDER_PAIR = 1
    FUN_SENDER_DPS = 2
    FUN_SENDER_DEVICE_STATUS = 3
    FUN_RECEIVE_TIME1_REQ = 32785
    FUN_RECEIVE_DP = 32769
###################################################################################################
class DpType(Enum):
    RAW = 0
    BOOLEAN = 1
    INT = 2
    STRING = 3
    ENUM = 4
    BIT_MAP = 5
###################################################################################################
#Fingerbot Plus
#reference: https://developer.tuya.com/en/demo/androidapp
class DpAction(Enum):
    TOGGLE_SWITCH = 2
    TIMER = 3
    MODE = 8
    ARM_DOWN_PERCENT = 9
    CLICK_SUSTAIN_TIME = 10
    INVERT_SWITCH = 11
    BATTERY_PERCENTAGE = 12
    ARM_UP_PERCENT = 15
    POWER_SAVING = 16
    TAP_ENABLE = 17
    CLICK = 101
    PROG = 121
###################################################################################################
class SecretKeyManager:
    def __init__(self, login_key):
        self.login_key = login_key

        self.keys = {
            4: hashlib.md5(self.login_key).digest(),
        }

    def get(self, security_flag):
        return self.keys.get(security_flag, None)

    def setSrand(self, srand):
        self.keys[5] = hashlib.md5(self.login_key + srand).digest()
###################################################################################################
class DeviceInfoResp:

    def __init__(self):
        self.success = False

    def parse(self, raw):
        device_version_major, device_version_minor, protocol_version_major, protocol_version_minor, flag, is_bind, srand, hardware_version_major, hardware_version_minor, auth_key = unpack('>BBBBBB6sBB32s', raw[:46])
        auth_key = hexlify(auth_key)
        # print(device_version_major, device_version_minor, protocol_version_major, protocol_version_minor, srand, hardware_version_major, hardware_version_minor, auth_key)

        self.device_version = '{}.{}'.format(device_version_major, device_version_minor)
        self.protocol_version = '{}.{}'.format(protocol_version_major, protocol_version_minor)
        self.flag = flag
        self.is_bind = is_bind
        self.srand = srand

        protocol_number = protocol_version_major * 10 + protocol_version_minor
        if protocol_number < 20:
            self.success = False
            return

        self.success = True
        return
###################################################################################################
class Ret:
    def __init__(self, raw, version):
        self.raw = raw
        self.version = version

    def parse(self, secret_key):
        self.security_flag = self.raw[0]
        self.iv = self.raw[1:17]
        encrypted_data = self.raw[17:]
        decrypted_data = AesUtils.decrypt(encrypted_data, self.iv, secret_key)

        sn, sn_ack, code, length = unpack('>IIHH', decrypted_data[:12])
        raw_data = decrypted_data[12:12 + length]
        #print(sn, sn_ack, code, length, raw_data)

        #s=binascii.hexlify(raw_data).decode('utf-8')
        #print(s)
        #sx = r"\x" + r"\x".join(s[n : n+2] for n in range(0, len(s), 2))
        #print(sx)

        self.resp = None
        try:
            self.code = Coder(code)
        except Exception:
            self.code = code

        if self.code == Coder.FUN_SENDER_DEVICE_INFO:
            resp = DeviceInfoResp()
            resp.parse(raw_data)
            self.resp = resp
###################################################################################################
class BleReceiver:
    def __init__(self, secret_key_manager):
        self.last_index = 0
        self.data_length = 0
        self.current_length = 0
        self.raw = bytearray()
        self.version = 0

        self.secret_key_manager = secret_key_manager

    def unpack(self, arr):
        i = 0
        packet_number = 0
        while i < 4 and i < len(arr):
            b = arr[i]
            packet_number |= (b & 255) << (i * 7)
            if ((b >> 7) & 1) == 0:
                break
            i += 1

        pos = i + 1
        if packet_number == 0:
            self.data_length = 0

            while (pos <= i + 4 and pos < len(arr)):
                b2 = arr[pos]
                self.data_length |= (b2 & 255) << (((pos - 1) - i) * 7)
                if (((b2 >> 7) & 1) == 0):
                    break
                pos += 1

            self.current_length = 0
            self.last_index = 0
            if (pos == i + 5 or len(arr) < pos + 2):
                return 2

            self.raw.clear()
            pos += 1
            self.version = (arr[pos] >> 4) & 15
            pos += 1

        if (packet_number == 0 or packet_number > self.last_index):
            data = bytearray(arr[pos:])
            self.current_length += len(data)
            self.last_index = packet_number
            self.raw += data

            if self.current_length < self.data_length:
                return 1

            return 0 if self.current_length == self.data_length else 3

    def parse_data_received(self, arr):
        status = self.unpack(arr)
        if status == 0:
            security_flag = self.raw[0]
            secret_key = self.secret_key_manager.get(security_flag)

            ret = Ret(self.raw, self.version)
            ret.parse(secret_key)

            return ret

        return None
###################################################################################################
class AesUtils:
    @staticmethod
    def decrypt(data, iv, key):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.decrypt(data)

    @staticmethod
    def encrypt(data, iv, key):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(data)
###################################################################################################
class CrcUtils:
    @staticmethod
    def crc16(data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte & 255
            for _ in range(8):
                tmp = crc & 1
                crc >>= 1
                if tmp != 0:
                    crc ^= 0xA001

        return crc
###################################################################################################
class TuyaDataPacket:
    @staticmethod
    def prepare_crc(sn_ack, ack_sn, code, inp, inp_length):
        raw = pack('>IIHH', sn_ack, ack_sn, code, inp_length)
        raw += inp
        crc = CrcUtils.crc16(raw)
        return raw + pack('>H', crc)

    @staticmethod
    def get_random_iv():
        return secrets.token_bytes(16)

    @staticmethod
    def encrypt_packet(secret_key, security_flag, iv, data):
        while len(data) % 16 != 0:
            data += b'\x00'

        encrypted_data = AesUtils.encrypt(data, iv, secret_key)
        output = bytearray()
        output += security_flag.to_bytes(1, byteorder='big')
        output += iv
        output += encrypted_data

        return output
###################################################################################################
class XRequest:
    def __init__(self, sn_ack, ack_sn, code, security_flag, secret_key, iv, inp):
        self.gatt_mtu = 20

        self.sn_ack = sn_ack
        self.ack_sn = ack_sn
        self.code = code
        self.security_flag = security_flag
        self.secret_key = secret_key
        self.iv = iv
        self.inp = inp


    def split_packet(self, protocol_version, data):
        output = []
        packet_number = 0
        pos = 0
        length = len(data)
        while pos < length:
            b = bytearray()
            b += packet_number.to_bytes(1, byteorder='big')

            if packet_number == 0:
                b += pack('>B', length)
                b += pack('<B', protocol_version << 4)

            sub_data = data[pos:pos + self.gatt_mtu - len(b)]
            b += sub_data
            output.append(b)

            pos += len(sub_data)
            packet_number += 1

        return output


    def pack(self):
        data = TuyaDataPacket.prepare_crc(self.sn_ack, self.ack_sn, self.code.value, self.inp, len(self.inp))
        encrypted_data = TuyaDataPacket.encrypt_packet(self.secret_key, self.security_flag, self.iv, data)

        return self.split_packet(2, encrypted_data)
###################################################################################################
class FingerBot:
    NOTIF_UUID = '00002b10-0000-1000-8000-00805f9b34fb'
    CHAR_UUID =  '00002b11-0000-1000-8000-00805f9b34fb'

    def __init__(self,
                 mac,
                 local_key,
                 uuid,
                 dev_id,
                 hci_device,
                 mode=0,
                 down_percent=80,
                 up_percent=60,
                 sustain_time=3,
                 switch_on_off=0,
                 switch_invert=False,
                 tap_enable=True):
        
        self.mac = mac
        self.uuid = uuid.encode('utf-8')
        self.dev_id = dev_id.encode('utf-8')
        self.login_key = local_key[:6].encode('utf-8')
        
        self.mode=mode
        self.down_percent=down_percent
        self.up_percent=up_percent
        self.sustain_time=sustain_time
        self.switch_on_off=switch_on_off
        self.switch_invert=switch_invert
        self.tap_enable=tap_enable

        self.secret_key_manager = SecretKeyManager(self.login_key)
        self.ble_receiver = BleReceiver(self.secret_key_manager)

        self.adapter = pygatt.GATTToolBackend(hci_device=hci_device)
        self.reset_sn_ack()
        self.isFingering=False

    def connect(self,timeout=5.0):
        try:
            log.info("Start ....")
            self.adapter.start(reset_on_start=False)
            #cost most time
            log.info('Connecting...')
            self.device=self.adapter.connect(self.mac,timeout, address_type=pygatt.BLEAddressType.public,auto_reconnect=False)
            return True
        except OSError as err:
            log.error("OS error:%s", err)
        except ValueError:
            log.error("Could not convert data to an integer.")
        except Exception as err:
            log.error("Exception:%s", err)
        
        self.adapter.stop()
        return False

    #block function
    def finger(self):
        try:
            self.device.subscribe(self.NOTIF_UUID, callback=self.handle_notification)
            req = self.device_info_request()
            self.send_request(req)

            while self.isFingering==False:
                time.sleep(0.1)

        finally:
            self.adapter.stop()
        

    def next_sn_ack(self):
        self.sn_ack += 1
        return self.sn_ack

    def reset_sn_ack(self):
        self.sn_ack = 0

    def handle_notification(self, handle, value):
        #print('<<', hexlify(value))
        ret = self.ble_receiver.parse_data_received(value)
        if not ret:
            return

        if ret.code == Coder.FUN_SENDER_DEVICE_INFO:
            self.secret_key_manager.setSrand(ret.resp.srand)

            log.info('Pairing...')
            req = self.pair_request()
            self.send_request(req)
            
        elif ret.code == Coder.FUN_SENDER_PAIR:          
            log.info('Fingering...')
            #switch/click
            dps = [
                [15, DpType.ENUM, 0],
                [DpAction.ARM_DOWN_PERCENT, DpType.INT, self.down_percent],
                [DpAction.ARM_UP_PERCENT, DpType.INT, self.up_percent],
                [DpAction.MODE, DpType.ENUM, self.mode],                   #0:click 1:switch
                [DpAction.CLICK_SUSTAIN_TIME, DpType.INT, self.sustain_time],
                [DpAction.CLICK, DpType.BOOLEAN, True],
                [DpAction.INVERT_SWITCH, DpType.ENUM, self.switch_invert], #0:positive 1:reverse 
                [DpAction.TOGGLE_SWITCH, DpType.BOOLEAN, self.switch_on_off],
                [DpAction.TAP_ENABLE, DpType.BOOLEAN, self.tap_enable],
                #[DpAction.BATTERY_PERCENTAGE, DpType.BOOLEAN, True]
            ]
            req = self.send_dps(dps)
            self.send_request(req)
            
            
        elif ret.code == Coder.FUN_RECEIVE_DP:
            self.isFingering=True

    def send_request(self, xrequest):
        packets = xrequest.pack()
        for cmd in packets:
            # print('  >>', hexlify(cmd))
            self.device.char_write(self.CHAR_UUID, value=cmd, wait_for_response=False)

    def device_info_request(self):
        security_flag = 4
        secret_key = self.secret_key_manager.get(security_flag)
        iv = TuyaDataPacket.get_random_iv()
        
        inp = bytearray(0)

        sn_ack = self.next_sn_ack()
        return XRequest(sn_ack=sn_ack, ack_sn=0, code=Coder.FUN_SENDER_DEVICE_INFO, security_flag=security_flag, secret_key=secret_key, iv=iv, inp=inp)

    def pair_request(self):
        security_flag = 5
        secret_key = self.secret_key_manager.get(security_flag)
        iv = TuyaDataPacket.get_random_iv()

        inp = bytearray()
        inp += self.uuid
        inp += self.login_key
        inp += self.dev_id

        for _ in range(22 - len(self.dev_id)):
            inp += b'\x00'

        sn_ack = self.next_sn_ack()
        return XRequest(sn_ack=sn_ack, ack_sn=0, code=Coder.FUN_SENDER_PAIR, security_flag=security_flag, secret_key=secret_key, iv=iv, inp=inp)


    def send_dps(self, _dps):
        security_flag = 5
        secret_key = self.secret_key_manager.get(security_flag)
        iv = TuyaDataPacket.get_random_iv()

        raw = b''
        for dp in _dps:
            dp_id, dp_type, dp_value = dp
            if isinstance(dp_id, Enum):
                dp_id = dp_id.value

            raw += pack('>BB', dp_id, dp_type.value)
            if dp_type == DpType.BOOLEAN:
                length = 1
                val = 1 if dp_value else 0
                raw += pack('>BB', length, val)
            elif dp_type == DpType.INT:
                length = 4
                raw += pack('>BI', length, dp_value)
            elif dp_type == DpType.STRING:
                length = len(dp_value)
                raw += pack('>B', length) + dp_value.encode('utf-8')
            elif dp_type == DpType.ENUM:
                length = 1
                raw += pack('>BB', length, dp_value)

        #print(hexlify(raw))
        sn_ack = self.next_sn_ack()
        return XRequest(sn_ack=sn_ack, ack_sn=0, code=Coder.FUN_SENDER_DPS, security_flag=security_flag, secret_key=secret_key, iv=iv, inp=raw)


    def disconnect(self):
        try:
            log.info('Disconnect...')
            self.adapter.stop()
            self.adapter.reset()
            log.info('Disconnect done...')
        except OSError as err:
            log.error("OS error:%s", err)
        except ValueError:
            log.error("Could not convert data to an integer.")
        except Exception as err:
            log.error("Exception:%s", err)
###################################################################################################