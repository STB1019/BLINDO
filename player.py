import os
import time
from machine import I2S, Pin
import math
import struct
from micropython import const
import gc
import array

class Player:
    START_TONES = const(((261, 150), (329, 150), (392, 200)))
    STOP_TONES = const(((392, 150), (329, 150), (261, 200)))
    START_SETUP_TONES = const(((261, 150), (329, 150), (392, 100), (440, 200)))
    STOP_SETUP_TONES = const(((440, 150), (392, 150), (329, 150), (261, 100)))
    VOLUME_UP_TONE = const(((1760, 50),))
    VOLUME_DOWN_TONE = const(((1318, 50),))
    ERROR_TONE = const(((150, 250),))
    SILENCE = bytearray(1000)

    def __init__(self, sck=19, ws=20, sd=21):
        self.i2s = None
        self.sck = sck
        self.ws = ws
        self.sd = sd
        self.volume = 0
        self.state = "DEINIT"
        self.source = None
        
        self.buf = bytearray()
        self.buf_mv = memoryview(self.buf)
        
    def prepare(self, freq, ibuf, buf, mono=True, irq=True):
        self.i2s = I2S(
            0,
            sck=Pin(self.sck),
            ws=Pin(self.ws),
            sd=Pin(self.sd),
            mode=I2S.TX,
            bits=16,
            format=I2S.MONO if mono else I2S.STEREO,
            rate=freq,
            ibuf=ibuf
        )
        if irq:
            self.i2s.irq(self.__irq)
        self.buf = bytearray(buf)
        self.buf_mv = memoryview(self.buf)
        self.state = "IDLE"
        
    def deinit(self):
        self.i2s.irq(None)
        self.i2s.deinit()
        self.buf = bytearray()
        self.buf_mv = memoryview(self.buf)
        gc.collect()
        self.state = "DEINIT"
        
    def adjust_volume(self, inc):
        self.volume += inc
        print(self.volume)
        
    def __irq(self, arg):
        if self.source is None:
            return
        if self.state == "PLAY":
            num_read = self.source.readinto(self.buf_mv)
            if num_read == 0:
                self.stop()
            else:
                I2S.shift(buf=self.buf_mv, bits=16, shift=self.volume)
                _ = self.i2s.write(self.buf_mv[:num_read])
        elif self.state == "IDLE":
            _ = self.i2s.write(Player.SILENCE)
        
    def play(self):
        if not self.state == "DEINIT":
            self.state = "PLAY"
    
    def pause(self):
        self.state = "IDLE"
        
    def stop(self):
        self.i2s.irq(None)
        self.deinit()
        if self.source is not None:
            self.source.close()
        
    def play_wav(self, filename):
        self.source = open(filename, "rb")
        
        assert self.source.read(4) == b"RIFF"
        samples = int.from_bytes(self.source.read(4), 'little') - 36
        assert self.source.read(8) == b"WAVEfmt "
        bits = int.from_bytes(self.source.read(4), 'little')
        assert bits == 16
        assert self.source.read(2) == b"\x01\x00"
        channels = int.from_bytes(self.source.read(2), 'little')
        rate = int.from_bytes(self.source.read(4), 'little')
        
        _ = self.source.seek(44)
        self.prepare(rate, 10240, 2048, mono=channels==1)
        self.i2s.write(Player.SILENCE)
        self.play()
        return rate, bits, channels, samples/(rate*channels*(bits//8))
        
    def play_tone(self, tones, rate=16000, ibuf=2000, samples=0):
        """
        tones: array of tuple (frequency (Hz), duration (ms))
        """
        if self.state == "DEINIT":
            self.prepare(rate, ibuf, samples, irq=False)
        else:
            self.pause()
            
        for freq, duration in tones:
            samples = Player.make_tone(rate, freq, self.volume)
            start_time = time.ticks_ms()
            while time.ticks_ms() - start_time < duration:
                _ = self.i2s.write(samples)
        
        if self.state == "DEINIT":
            self.deinit()
        else:
            self.play()
    
    @staticmethod
    def make_tone(rate, frequency, volume):
        samples_per_cycle = rate // frequency
        samples = bytearray(samples_per_cycle * 2)
        range = 65535 // 16
        for i in range(samples_per_cycle):
            sample = range + int((range - 1) * math.sin(2 * math.pi * i / samples_per_cycle))
            struct.pack_into("<h", samples, i * 2, sample)
        I2S.shift(buf=samples, bits=16, shift=volume)
        return samples
