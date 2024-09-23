from Light import Light
from lib.ha_mqtt_device import Device
from lib.lib.mqtt_as import MQTTClient
from lib.wifiConfig import tryConnectingToKnownNetworks
from secrets import mqtt_password, mqtt_user
import uasyncio
from lib.neopixel import Neopixel

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

ha_light = Light(
    mqtt=client,
    name=b'light',
    device=device,
    transition_duration_ms=500,
    frame_duration_ms=frame_duration_ms
)

async def mqtt_up():
    await client.connect()
    await ha_light.init_mqtt()
    while True:
        await client.up.wait() # type: ignore
        client.up.clear()
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

    while True:
        if ha_light.is_on:
            lights.fill(ha_light.color.to_tuple())
            lights.brightness(ha_light.brightness)
        else:
            lights.fill((0,0,0))

        lights.show()
        await uasyncio.sleep_ms(frame_duration_ms)

async def main():
    _, ssid, password = await tryConnectingToKnownNetworks()
    client._ssid = ssid
    client._wifi_pw = password
    await uasyncio.gather(mqtt_messages_handler(), mqtt_up(), lights_main()) # type: ignore

uasyncio.run(main())
