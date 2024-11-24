import ujson as json
import re

row_regex = re.compile("(\\d+)r\\[(.*)\\]\n?")
value_regex = re.compile("(\\d+)x(\\d+)")

def parse_value(val: str, color_table):
    result = re.match(value_regex, val)

    if result:
        count, num = result.groups()
        for _ in range(int(count)):
            yield color_table[int(num)]
    else:
        yield color_table[int(val)]

def parse_row(row: str, color_table):
    for val in row.split(','):
        yield from parse_value(val, color_table)

def parse_rows(f):
    for row in f:
        result = re.match(row_regex, row)
        if result:
            count, rest = result.groups()
            for _ in range(int(count)):
                yield rest
        else:
            yield row

class effect_reader:
    def __init__(self, filename: str, effect_name: str):
        self.effect_name = effect_name
        self.filename = filename

        with open(filename, 'r') as f:
            self.metadata = json.loads(next(f))

        self.frame_delay_ms = self.metadata['frame_delay_ms']
        self.light_count = self.metadata['light_count']

    def read_frames(self):
        with open(self.filename, 'r') as f:
            while True:
                next(f)
                for row in parse_rows(f):
                    yield parse_row(row, self.metadata['colors'])

                f.seek(0)
