import os
import time
from machine import I2S, Pin
import math
import struct
from micropython import const
import gc
import array

class Recorder:
    def __init__(self, sck=16, ws=17, sd=18):
        self.i2s = None
        self.sck = sck
        self.ws = ws
        self.sd = sd
        self.state = "DEINIT"
        self.dest = None
        
        self.buf = array.array('H', [0] * 1024)
        self.buf_mv = memoryview(self.buf)
        
        self.samples = 0
        self.last_read = 0
        self.filename = ""
        
    def prepare(self):
        self.i2s = I2S(
            0,
            sck=Pin(self.sck),
            ws=Pin(self.ws),
            sd=Pin(self.sd),
            mode=I2S.RX,
            bits=16,
            format=I2S.MONO,
            rate=8000,
            ibuf=40000
        )
        self.i2s.irq(self.__irq)
        self.state = "IDLE"
        
    def deinit(self):
        self.i2s.irq(None)
        self.i2s.deinit()
        gc.collect()
        self.state = "DEINIT"
        
    def __irq(self, arg):
        if self.state == "REC":
            written = self.dest.write(self.buf_mv[:self.last_read])
            self.samples += written
            self.last_read = self.i2s.readinto(self.buf_mv)
        elif self.state == "RESUME":
            self.state = "REC"
            self.last_read = self.i2s.readinto(self.buf_mv)
        elif self.state == "IDLE":
            _ = self.i2s.readinto(self.buf_mv)
        
    def resume(self):
        if self.state == "IDLE":
            self.state = "RESUME"
    
    def pause(self):
        self.state = "IDLE"
        
    def stop(self, normalize=True):
        self.i2s.irq(None)
        self.i2s.deinit()
        gc.collect()
        time.sleep(0.2)
        self.dest.flush()
        self.dest.seek(0)
        _ = self.dest.write(Recorder.create_wav_header(8000, 16, 1, self.samples))
        self.dest.flush()
        
        if normalize:
            self.normalize()
        self.dest.close()

        rec_sec = self.samples / (8000*2)
        self.dest = None                                
        self.samples = 0
        self.last_read = 0
        self.filename = ""
        return rec_sec
        
    def normalize(self):
        self.dest.seek(44)
        
        #Workaround for philips i2s timings
        n = 0
        while True:
            read = self.dest.readinto(self.buf_mv)
            if read == 0:
            	break
            _ = self.dest.seek(n+44)
            
            for i in range(int(read/2)):
            	self.buf_mv[i] = self.buf_mv[i] << 1
            _ = self.dest.write(self.buf_mv)
            n += read
        
    def start(self, filename):
        self.dest = open(filename, 'wb+')
        self.filename = filename
        self.prepare()
        self.last_read = self.i2s.readinto(self.buf_mv)
        time.sleep(0.5)
        self.state = "REC"
        
    @staticmethod
    def create_wav_header(sampleRate, bitsPerSample, num_channels, num_samples):
        datasize = num_samples * num_channels * bitsPerSample // 8
        o = bytes("RIFF", "ascii")  # (4byte) Marks file as RIFF
        o += (datasize + 36).to_bytes(
            4, "little"
        )  # (4byte) File size in bytes excluding this and RIFF marker
        o += bytes("WAVE", "ascii")  # (4byte) File type
        o += bytes("fmt ", "ascii")  # (4byte) Format Chunk Marker
        o += (16).to_bytes(4, "little")  # (4byte) Length of above format data
        o += (1).to_bytes(2, "little")  # (2byte) Format type (1 - PCM)
        o += (num_channels).to_bytes(2, "little")  # (2byte)
        o += (sampleRate).to_bytes(4, "little")  # (4byte)
        o += (sampleRate * num_channels * bitsPerSample // 8).to_bytes(4, "little")  # (4byte)
        o += (num_channels * bitsPerSample // 8).to_bytes(2, "little")  # (2byte)
        o += (bitsPerSample).to_bytes(2, "little")  # (2byte)
        o += bytes("data", "ascii")  # (4byte) Data Chunk Marker
        o += (datasize).to_bytes(4, "little")  # (4byte) Data size in bytes
        return o
        
    
