from Color import Color
from Light import Light
from effect_reader import effect_reader
from lib.ha_mqtt_device import Device
from lib.lib.mqtt_as import MQTTClient
from lib.wifiConfig import tryConnectingToKnownNetworks
from sdcard import SDCard
from secrets import mqtt_password, mqtt_user
import uasyncio
from lib.neopixel import Neopixel
import machine
import uos
import time
import gc

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

sd = None

try:
    sd = SDCard(spi, chipSelectPin)
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, "/sd")
except:
    pass

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

effect_filenames = []
try:
    effect_filenames = [filename.rsplit('.') for filename in uos.listdir('/sd/effects')]
except:
    pass

ha_light = Light(
    mqtt=client,
    name=b'light',
    device=device,
    transition_duration_ms=500,
    frame_duration_ms=frame_duration_ms,
    effects=[filename for (filename, extension) in effect_filenames if extension == 'effect']
)

async def mqtt_up():
    await client.connect()
    await device.init_mqtt()
    await ha_light.init_mqtt()
    while True:
        await client.up.wait() # type: ignore
        client.up.clear()
        await device.init_mqtt()
        await ha_light.init_mqtt()

async def mqtt_messages_handler():
    async for topic, msg, retained in client.queue: # type: ignore
        await ha_light.handle_mqtt_message(topic, msg)

async def lights_main():
    lights = Neopixel(
        num_leds=100,
        pin=22,
        state_machine=0,
    )
    reader = None
    frames = None

    while True:
        if not ha_light.effect:
            lights.fill(ha_light.color.to_tuple(), ha_light.brightness)
            await uasyncio.sleep_ms(frame_duration_ms)
        else:
            last_frame_time_ms = time.ticks_ms()
            try:
                if not reader or reader.effect_name != ha_light.effect:
                    reader = effect_reader(
                        effect_name=ha_light.effect,
                        filename=f'/sd/effects/{ha_light.effect}.effect',
                    )
                    frames = reader.read_frames()
                    gc.collect()

                frame = next(frames) #type:ignore

                for i, val in enumerate(frame):
                    lights.set_pixel(i, val, ha_light.brightness)
            except OSError as e:
                print(e)
                ha_light.effect = None
                await ha_light.publish_state(ha_light.brightness, ha_light.color)

            delay = reader.frame_delay_ms if reader else frame_duration_ms

            diff = time.ticks_diff(time.ticks_ms(), last_frame_time_ms)

            if delay - diff > 0:
                await uasyncio.sleep_ms(delay - diff)
            else:
                await uasyncio.sleep_ms(2)

        lights.show()


async def main():
    _, ssid, password = await tryConnectingToKnownNetworks()
    client._ssid = ssid
    client._wifi_pw = password
    await uasyncio.gather(mqtt_messages_handler(), mqtt_up(), lights_main()) # type: ignore

uasyncio.run(main())
