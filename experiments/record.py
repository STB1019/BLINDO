import os
import time
import micropython
from machine import I2S, Pin, SPI, I2C
from sdcard import SDCard
import gc
from ssd1306 import SSD1306_I2C
import array

cs = Pin(15, machine.Pin.OUT)
spi = SPI(1, baudrate=1400000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
sd = SDCard(spi, cs, baudrate=15500000)
fs = os.VfsFat(sd)
os.mount(sd, "/sd")

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
    
wav = open("/sd/recb.wav", "wb")

RECORDING_SIZE_IN_BYTES = (
    15 * 8000 * 2
)
    
audio_in = I2S(
    0,
    sck=Pin(16),
    ws=Pin(17),
    sd=Pin(18),
    mode=I2S.RX,
    bits=16,
    format=I2S.MONO,
    rate=8000,
    ibuf=65536,
)

mic_samples = bytearray(2048)
mic_samples_mv = memoryview(mic_samples)
num_bytes_written = wav.write(create_wav_header(8000, 16, 1, 8000*240))
num_sample_bytes_written_to_wav = 0

try:
	t_start = time.ticks_ms()
    while num_sample_bytes_written_to_wav < RECORDING_SIZE_IN_BYTES:
    	secs = int((time.ticks_ms() - t_start)/1000)
        num_bytes_read_from_mic = audio_in.readinto(mic_samples_mv)
        if secs < 0.5:
    		continue
        if num_bytes_read_from_mic > 0:
            num_bytes_written = wav.write(mic_samples_mv[:num_bytes_read_from_mic])
            num_sample_bytes_written_to_wav += num_bytes_written
    print("==========  DONE RECORDING ==========")
except (KeyboardInterrupt, Exception) as e:
    print("caught exception {} {}".format(type(e).__name__, e))
    
wav.close()
audio_in.deinit()
del audio_in
del mic_samples
del mic_samples_mv
gc.collect()

#dest = open("/sd/orig.wav", "wb")
#wav = open("/sd/recb.wav", "rb")
#tot = 0
buf = array.array('h', [0]*1024)
mv = memoryview(buf)
#while True:
#    read = wav.readinto(mv)
#    if read > 0:
#        _ = dest.write(mv)
#        tot += read
#        print(f"COPIED {tot/1024}      \r", end="")
#        continue
#    print()
#    break
#wav.close()
#dest.close()

wav = open("/sd/recb.wav", "r+")
wav.seek(44)

minimum = 65536
maximum = -65536
offset = 0
n = 0

size = os.stat("/sd/recb.wav")[6] - 44
oled.fill(0)
oled.text("Saving...", 1, 2)
oled.show()
    	
while True:
    read = wav.readinto(mv)
    if read == 0:
    	print()
    	break
    minimum = min(minimum, min(mv))
    maximum = max(maximum, max(mv))
    offset = ((offset * n) + (sum(mv)))/(n+read/2)
    n += read/2
    oled.fill(0)
    oled.text("Saving...", 1, 1)
	oled.text("{:3.2f}".format(n/size*100), 1, 2)
	oled.show()
    print(f"{minimum} {maximum} {offset} {n*2/size*100}%          \r", end="")

wav.seek(44)

norm_min = abs(minimum - offset)
norm_max = abs(maximum - offset)
gain = 32767 / max(norm_min, norm_max)

n = 0
while True:
    read = wav.readinto(mv)
    if read == 0:
    	print()
    	break
    _ = wav.seek(n+44)
    
    for i in range(int(read/2)):
    	mv[i] = int((mv[i] - offset) * gain)
    
    _ = wav.write(mv)
    n += read
    oled.fill(0)
    oled.text("Saving...", 1, 1)
	oled.text("Saving... {:3.2f}".format(n/2/size*100 + 50), 1, 1)
	oled.show()
    print(f"{n/size*100}%          \r", end="")

wav.close()
	
