from machine import Pin, WDT
from usrio.usrio import UsrIO
from usrio.usrio_conf import UsrIOConfig
from machine import Pin, I2C, SPI
from ui.ssd1306_ui import SSD1306UI
from ui.views.fatal import FatalView
from ui.primitives.text import Text
import os
from sdcard import SDCard
import time
from player import Player
from recorder import Recorder
import micropython
import gc

class SM:
    def __init__(self, io, ui):
        self.io = io
        self.ui = ui
        try:
            cs = Pin(13, machine.Pin.OUT)
            self.spi = SPI(1, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
            self.sd = SDCard(self.spi, cs, baudrate=10000000)
            self.fs = os.VfsFat(self.sd)
            os.mount(self.sd, "/sd")
        except OSError as e:
            FatalView(self.ui, e.value).show()
            while True:
                time.sleep(1)
        
    def terminate(self):
        os.umount("/sd")
        self.spi.deinit()
        ui.display.fill(0)
        ui.display.show()


class UseSM(SM):
    def __init__(self, io, ui):
        super(UseSM, self).__init__(io, ui)
        self.player = None
        self.cur_sel = -1

    def _irq_volume(self, inc=0):
        self.player.adjust_volume(inc)
        if self.player.state != 'PLAY':
            self.player.play_tone(Player.VOLUME_UP_TONE if inc > 0 else Player.VOLUME_DOWN_TONE)
    
    def _irq_select(self, foo, selected):
        if self.player.state == 'DEINIT':
            self.cur_sel = -1
            
        self.ui.display.fill(0)
        self.ui.display.show()
        
        if selected != self.cur_sel:
            self.player.stop()
            try:
                self.player.play_wav(f"/sd/{selected}.wav")
                self.cur_sel = selected
            except:
                FatalView(self.ui, "no file").show()
                self.player.play_tone(Player.ERROR_TONE)
        else:
            if self.player.state == 'PLAY':
                self.player.pause()
            else:
                self.player.play()
                
                
    def init_and_run(self, *args, **kwargs):
        self.player = Player()
        self.player.play_tone(Player.START_TONES)
                
        self.io.on_volume = self._irq_volume
        self.io.config.USR_BTNS.irq = self._irq_select
        
    def terminate(self):
        self.player.play_tone(Player.STOP_TONES)
        self.player.deinit()
        self.io.on_volume = None
        self.io.config.USR_BTNS.irq = None
        super().terminate()
        
        
class SetupSM(SM):
    def __init__(self, io, ui):
        super(UseSM, self).__init__(io, ui)
        self.player = None
        self.recorder = None
        self.action_text = Text(4, 4, "IDLE")
        self.rec_time = Text(4, 14, "00:00")
        self.cur_sel = -1
    
    def _irq_select(self, foo, selected):
        if self.cur_sel == -1:
            self.recorder.start(f"/sd/{selected}.wav")
            self.action_text.set_text("RECORDING")
            self.cur_sel = selected
        else:
            self.action_text.set_text("SAVING")
            self.ui.redraw()
            self.recorder.stop(normalize=False)
            self.action_text.set_text("IDLE")
            self.ui.redraw()
            self.cur_sel = -1
            
        
    def init_and_run(self, *args, **kwargs):
        self.player = Player()
        self.recorder = Recorder()
        
        self.ui.add(self.action_text)
        self.ui.add(self.rec_time)
        self.ui.redraw()
        
        self.player.play_tone(Player.START_SETUP_TONES)
        self.io.config.USR_BTNS.irq = self._irq_select
    
    def terminate(self):
        self.io.config.USR_BTNS.irq = None
        super().terminate()
        
#wdt = WDT(timeout=4000)
io = UsrIO(UsrIOConfig())
#init display
ui = SSD1306UI(I2C(1, sda=Pin(14), scl=Pin(15), freq=400000))

stdby_led = machine.Pin('LED', machine.Pin.OUT)
sm = None

def on_pwr_on():
    global sm
    machine.freq(133_000_000)
    stdby_led.off()
    if io.config.VOL_UP_PIN.value() == 0:
        sm = SetupSM(io, ui)
    else:
        sm = UseSM(io, ui)
    micropython.schedule(sm.init_and_run, None)
	
def on_pwr_off():
    global sm
    sm.terminate()
    stdby_led.on()
    machine.freq(20_000_000)
    
	
io.on_power_on=on_pwr_on
io.on_power_off=on_pwr_off

#while True:
#   wdt.feed()

