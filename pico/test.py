import machine
from sdcard import SDCard
import uos

chipSelectPin = machine.Pin(17, machine.Pin.OUT)
spi = machine.SPI(
    0,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    bits=8,
    firstbit=machine.SPI.MSB,
    sck=machine.Pin(18),
    mosi=machine.Pin(19),
    miso=machine.Pin(16)
)

card = SDCard(spi, chipSelectPin)

vfs = uos.VfsFat(card)
uos.mount(vfs, "/sd")

