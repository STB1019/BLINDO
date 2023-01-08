import os
import time
import micropython
from machine import I2S, Pin, SPI
from sdcard import SDCard

cs = Pin(15, machine.Pin.OUT)

def init(cs, init_freq, freq):
    spi = None
    try:
        spi = SPI(1, baudrate=init_freq*1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
        sd = SDCard(spi, cs, baudrate=freq*1000000)
        return sd, spi
    except:
	    spi.deinit()
	    return
	    
def test(sd):
    fs = os.VfsFat(sd)
    os.mount(fs, '/sd')
    print("writing")
    s = 0
    dat = bytes([i%256 for i in range(4096)])
    for i in range(10):
        f = open('/sd/wrt', 'wb')
        a = time.ticks_us()
        f.write(dat)
        s += time.ticks_us() - a
        f.close()
    print(f"Write speed: 4k in {s/10}us => {4096/((s/10 + 1)/1000)*1000}")
    s = 0
    dat2 = None
    for i in range(10):
        f = open('/sd/wrt', 'rb')
        a = time.ticks_us()
        dat2 = f.read(4096)
        s += time.ticks_us() - a
        f.close()
    print(f"Read speed: 4k in {s/10}us => {4096/((s/10 + 1)/1000)*1000}") 
    print(list(fs.ilistdir()))
    os.umount('/sd')
    del fs
    return dat, dat2

def deinit(sd, spi):
     spi.deinit()
     del sd
     
sd, spi = init(cs, 10, 15)
test(sd)
deinit(sd, spi)
