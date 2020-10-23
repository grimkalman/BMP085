import smbus
import RPi.GPIO as gpio
import time

# Register addresses
CONTROL = 0xF4

class bmp085():

    def __init__(self, device_address, bus=1):
        # Open communications
        self.bus = smbus.SMBus(bus)
        self.address = device_address
        
        # Load factory calibration coefficients
        self.AC1 = self.load_coefficient(0xAA, 1)
        self.AC2 = self.load_coefficient(0xAC, 1)
        self.AC3 = self.load_coefficient(0xAE, 1)
        self.AC4 = self.load_coefficient(0xB0, 0)
        self.AC5 = self.load_coefficient(0xB2, 0)
        self.AC6 = self.load_coefficient(0xB4, 0)
        self.B1 = self.load_coefficient(0xB6, 1)
        self.B2 = self.load_coefficient(0xB8, 1)
        self.MB = self.load_coefficient(0xBA, 1)
        self.MC = self.load_coefficient(0xBC, 1)
        self.MD = self.load_coefficient(0xBE, 1)
        
    def load_coefficient(self, address, signed):
        # Read the register
        hi, lo = self.bus.read_i2c_block_data(self.address, address, 2)
        
        # Merge high  bits with low bits
        value  = (hi << 8) | lo
        
        # If signed == 1 and value > 32768
        if signed and value & 0x8000:
            
            # Get signed data
            value -= 0x10000   
        return value
        
    def read_raw_temp(self):
        # Begin measurement (this command needs to be sent every time)
        self.bus.write_byte_data(self.address, CONTROL, 0x2E)
        
        # Wait 4.5 ms
        time.sleep(0.0045)
        
        # Read sensor
        hi, lo = self.bus.read_i2c_block_data(self.address, 0xF6, 2)
        
        # Merge high bits with low bits
        value = (hi << 8) | lo
        
        # Get signed data
        if value & 0x8000:  # (faster than compare)
                value -= 0x10000
        return value
    
    def read_raw_pressure(self):
        # Begin measurement (this command needs to be sent every time)
        self.bus.write_byte_data(self.address, CONTROL, 0x74)
        
        # Wait 7.5 ms
        time.sleep(0.0075)
        
        # Read sensor
        hi, lo, xlo = self.bus.read_i2c_block_data(self.address, 0xF6, 3)
        
        # Merge high bits with low bits
        value = ((hi << 16) | (lo << 8) | xlo) >> 7
        
        # Get signed data
        if value & 0x8000:  # (faster than compare)
                value -= 0x10000
        return value
    
    def get_pressure(self):
        # Convert raw temp and pressure to Pa using the formula described in the datasheet
        x1 = (self.read_raw_temp() - self.AC6) * self.AC5 / 32768
        x2 = self.MC * (2048) / (x1 + self.MD)
        b5 = x1 + x2
        b6 = b5 - 4000
        x1 = (self.B2 * (b6 ** 2 / (4096))) / (2048)
        x2 = self.AC2 * b6 / (2048)
        x3 = x1 + x2
        b3 = ((int(self.AC1 * 4 + x3) << 1) + 2) / 4
        x1 = self.AC3 * b6 / (8192)
        x2 = (self.B1 * (b6 ** 2 / 4096)) / 65536
        x3 = ((x1 + x2) + 2) / 4
        b4 = self.AC4 * (x3 + 32768) / (32768)
        b7 = (self.read_raw_pressure() - b3) * 25000

        if(b7 < 0x800000000):
            p = (b7 * 2) / b4
        else:
            p = (b7 / b4) * 2
            
        x1 = (p / 256) * (p / 256)
        x1 = (x1 * 3038) / 65536
        x2 = (-7357 * p) / 65536
        
        return p + (x1 + x2 + 3791) / (2 ** 4)
    
    def get_altitude(self):
        return 44330 * (1 - ((self.get_pressure() / 101325) ** (0.19029495718363465)))
