import os
import time
import micropython
from machine import I2S, Pin, SPI
from sdcard import SDCard

cs = Pin(13, machine.Pin.OUT)
spi = SPI(1, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
sd = SDCard(spi, cs, baudrate=12000000)
fs = os.VfsFat(sd)
os.mount(sd, "/sd")
for i in os.ilistdir('/sd'):
    print(i)

from recorder import Recorder
r = Recorder()
r.start("/sd/test.wav")

from player import Player
p = Player()
p.play_wav('/sd/test.wav')


audio_out = I2S( 
    1,
    sck=Pin(19),
    ws=Pin(20),
    sd=Pin(21),
    mode=I2S.TX,
    bits=16,
    format=I2S.STEREO,
    rate=44100,
    ibuf=60000,
)

wav = open("/sd/test_stereo_44.wav", "rb")
_ = wav.seek(44)

wav_samples = bytearray(20000)
wav_samples_mv = memoryview(wav_samples)
shift = 0

try:
    while True:
        num_read = wav.readinto(wav_samples_mv)
        if num_read == 0:
            break
        else:
        	I2S.shift(buf=wav_samples_mv[:num_read], bits=16, shift=1)
            _ = audio_out.write(wav_samples_mv[:num_read])
except (KeyboardInterrupt, Exception) as e:
    print("caught exception {} {}".format(type(e).__name__, e))

