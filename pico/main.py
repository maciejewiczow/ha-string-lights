from os import listdir
from Light import Light
from lib.ha_mqtt_device import Device
from lib.lib.mqtt_as import MQTTClient
from lib.wifiConfig import tryConnectingToKnownNetworks
from sdcard import SDCard
from secrets import mqtt_password, mqtt_user
import uasyncio
from lib.neopixel import Neopixel
import machine
import uos

# chipSelectPin = machine.Pin(17, machine.Pin.OUT)
# spi = machine.SPI(
#     0,
#     baudrate=1_000_000,
#     polarity=0,
#     phase=0,
#     bits=8,
#     firstbit=machine.SPI.MSB,
#     sck=machine.Pin(18),
#     mosi=machine.Pin(19),
#     miso=machine.Pin(16)
# )

# sd = None

# try:
#     sd = SDCard(spi, chipSelectPin)
#     vfs = uos.VfsFat(sd)
#     uos.mount(vfs, "/sd")
# except:
#     pass

frame_duration_ms = 30

client = MQTTClient(
    port=1883,
    user=mqtt_user,
    password=mqtt_password,
    server='192.168.88.19',
    queue_len=10,
    ssid='',
    wifi_pw=''
)

device = Device(
    mqtt=client,
    device_id=b'rpi_string_lights',
    manufacturer=b'DIY',
    model=b'Raspberry Pi PICO',
    name=b'String lights',
)

# effect_filenames = []
# try:
#     effect_filenames = uos.listdir('/sd/effects')
# except:
#     pass

ha_light = Light(
    mqtt=client,
    name=b'light',
    device=device,
    transition_duration_ms=500,
    frame_duration_ms=frame_duration_ms,
    # effects=[filename.rsplit('.')[0] for filename in effect_filenames]
)

async def mqtt_up():
    await client.connect()
    await ha_light.init_mqtt()
    await device.init_mqtt()
    while True:
        await client.up.wait() # type: ignore
        client.up.clear()
        await ha_light.init_mqtt()
        await device.init_mqtt()

async def mqtt_messages_handler():
    async for topic, msg, retained in client.queue: # type: ignore
        await ha_light.handle_mqtt_message(topic, msg)

async def lights_main():
    lights = Neopixel(
        num_leds=100,
        pin=22,
        state_machine=0,
    )

    while True:
        lights.fill(ha_light.color.to_tuple(), ha_light.brightness)
        lights.show()

        await uasyncio.sleep_ms(frame_duration_ms)

async def main():
    _, ssid, password = await tryConnectingToKnownNetworks()
    client._ssid = ssid
    client._wifi_pw = password
    await uasyncio.gather(mqtt_messages_handler(), mqtt_up(), lights_main()) # type: ignore

uasyncio.run(main())
