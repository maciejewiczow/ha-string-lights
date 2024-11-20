from Color import Color
from lib.ha_mqtt_device import BaseEntity, Device, MQTTClient
import uasyncio
import ujson as json
from ubinascii import hexlify
import machine
from uasyncio import create_task, CancelledError, sleep_ms
import math

class Light(BaseEntity):
    def __init__(
        self,
        mqtt: MQTTClient,
        *,
        name: bytes,
        device: Device,
        object_id = None,
        effects = [],
        unique_id = None,
        node_id = None,
        discovery_prefix = b'homeassistant',
        extra_conf = None,
        transition_duration_ms = 500,
        frame_duration_ms = 30
    ):
        cmd_t_suffix = b'set'

        hardwareId = hexlify(machine.unique_id())

        objectid = object_id if object_id else b'light-' + hardwareId #type: ignore

        config = {
            'cmd_t': b'~/' + cmd_t_suffix,
            'uniq_id': unique_id if unique_id else objectid, # type: ignore
            'schema': 'json',
            'brightness': True,
            'supported_color_modes': ['rgb'],
        }

        self.effect = None
        self.possible_effects = effects
        self.is_on = True
        self.color = Color.rgb(1, 1, 1)
        self.brightness = 255
        self.transition_duration_ms = transition_duration_ms
        self.frame_duration_ms = frame_duration_ms
        self.brightness_transition_task = None
        self.color_transition_task = None

        if len(effects) > 0:
            config['effect_list'] = effects
            config['effect'] = True

        if extra_conf:
            config.update(extra_conf)

        super().__init__(
            mqtt,
            name,
            component=b'light',
            device=device,
            object_id=objectid,
            node_id=node_id,
            discovery_prefix=discovery_prefix,
            extra_conf=config
        )

        self.command_topic = self.base_topic + b'/' + cmd_t_suffix

    async def init_mqtt(self):
        await super().init_mqtt()
        await self.mqtt.subscribe(self.command_topic)
        await self.publish_state()

    async def handle_mqtt_message(self, topic: bytes, message):
        if topic == self.command_topic:
            await self._handle_command(message)

    async def _color_transition(self, start_color, target_color):
        try:
            total_frames = math.ceil(self.transition_duration_ms/self.frame_duration_ms)
            for frame in range(total_frames):
                self.color = start_color.blend(target_color, frame/total_frames)
                await sleep_ms(self.frame_duration_ms)

        except CancelledError:
            pass

    async def _brightness_transition(self, start_brightness, target_brightness):
        try:
            totalFrames = math.ceil(self.transition_duration_ms/self.frame_duration_ms)
            for frame in range(totalFrames):
                frac = frame/totalFrames

                self.brightness = int(start_brightness * (1 - frac) + target_brightness * frac)

                await sleep_ms(self.frame_duration_ms)

        except CancelledError:
            pass

    async def start_brightness_transition(self, target_brightness):
        if self.brightness_transition_task:
            self.brightness_transition_task.cancel() # type: ignore

        self.brightness_transition_task = create_task(
            self._brightness_transition(
                start_brightness=self.brightness,
                target_brightness=target_brightness,
            )
        )
        await self.publish_state(target_brightness, None)

    async def start_color_transition(self, target_color):
        if self.color_transition_task:
            self.color_transition_task.cancel() # type: ignore

        self.color_transition_task = create_task(
            self._color_transition(
                start_color=self.color,
                target_color=target_color,
            )
        )
        await self.publish_state(None, target_color)

    async def publish_state(self, brightness = None, color = None):
        state = {
            'state': b'ON' if self.is_on else b'OFF',
            'brightness': brightness if brightness else self.brightness,
            'color': dict(color if color else self.color)
        }

        if self.effect:
            state['effect'] = self.effect

        await super().publish_state(json.dumps(state))

    async def _handle_command(self, raw_message):
        try:
            message = json.loads(raw_message.decode())
        except ValueError:
            print("Invalid json command")
            return

        is_on = message.get('state', None)
        brightness = message.get('brightness', None)
        effect = message.get('effect', None)
        color = message.get('color', None)

        if is_on:
            self.is_on = is_on == 'ON'

        if effect is None:
            self.effect = None
        elif effect in self.possible_effects:
            self.effect = effect
        else:
            print(f'Unavailable effect recieved: {effect}')

        bright_coro, color_coro = None, None
        if brightness:
            bright_coro = self.start_brightness_transition(brightness)

        if color:
            color_coro = self.start_color_transition(Color.from_dict(color))

        if bright_coro and color_coro:
            await uasyncio.gather(bright_coro, color_coro)  # type: ignore
        elif color_coro:
            await color_coro
        elif bright_coro:
            await bright_coro
