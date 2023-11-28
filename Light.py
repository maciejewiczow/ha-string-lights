from lib.ha_mqtt_device import BaseEntity, MQTTClient
import ujson as json
from ubinascii import hexlify
import machine

class Light(BaseEntity):
    payload_available = b'1'
    payload_unavailable = b'0'

    def __init__(
        self,
        mqtt: MQTTClient,
        name: bytes,
        object_id = None,
        device = None,
        effects = [],
        unique_id = None,
        node_id = None,
        discovery_prefix = b'homeassistant',
        extra_conf = None
    ):
        cmd_t_suffix = b'set'
        avail_t_suffix = b'avail'

        hardwareId = hexlify(machine.unique_id())

        objectid = object_id if object_id else b'light-' + hardwareId #type: ignore

        config = {
            'cmd_t': b'~/' + cmd_t_suffix,
            'uniq_id': unique_id if unique_id else objectid, # type: ignore
            'schema': 'json',
            'availability': {
                'payload_available': self.payload_available,
                'payload_not_available': self.payload_unavailable,
                'topic': b'~/' + avail_t_suffix
            },
            'brightness': True,
            'rgb': True,
        }

        self.effect = None
        self.possible_effects = effects
        self.is_on = True
        self.color = (255, 255, 255)
        self.brightness = 255

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

        self.avail_topic = self.base_topic + b'/' + avail_t_suffix
        self.command_topic = self.base_topic + b'/' + cmd_t_suffix

    async def init_mqtt(self):
        await super().init_mqtt()
        await self._publish_available()
        self.mqtt.set_last_will(self.avail_topic, self.payload_unavailable)
        await self.mqtt.subscribe(self.command_topic)
        await self.mqtt.subscribe(b'homeassistant/status')
        await self.publish_state()

    async def _publish_available(self):
        await self.mqtt.publish(self.avail_topic, self.payload_available)

    async def handle_mqtt_message(self, topic: bytes, message):
        if topic == self.command_topic:
            await self._handle_command(message)
        elif topic == b'homeassistant/status' and message == b'online':
            await self._handle_ha_start()

    async def publish_state(self):
        state = {
            'state': b'ON' if self.is_on else b'OFF',
            'brightness': self.brightness,
            'color': {
                'r': self.color[0],
                'g': self.color[1],
                'b': self.color[2]
            }
        }

        if self.effect:
            state['effect'] = self.effect

        await super().publish_state(json.dumps(state))

    async def _handle_ha_start(self):
        await self._publish_available()
        await self.publish_state()

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

        if brightness:
            self.brightness = brightness

        if effect is None:
            self.effect = None
        elif effect in self.possible_effects:
            self.effect = effect
        else:
            print(f'Unavailable effect recieved: {effect}')

        if color:
            try:
                r = color['r']
                g = color['g']
                b = color['b']
                self.color = (r, g, b)
            except KeyError:
                print('Malformed color value received')

        await self.publish_state()
