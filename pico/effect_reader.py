import ujson as json


class effect_reader:
    def __init__(self, filename: str, effect_name: str, batch_size = 20):
        self.batch_size = batch_size
        self.filename = filename
        self.effect_name = effect_name

        with open(filename, 'r') as f:
            metadata = json.loads(next(f))

        self.frame_delay_ms = metadata['frame_delay_ms']
        self.light_count = metadata['light_count']

    def read_frames(self):
        with open(self.filename, 'r') as f:
            while True:
                next(f)

                batch = []
                for row in f:
                    batch.append([int(value) for i,value in enumerate(row.split(',')) if i < self.light_count])

                    if len(batch) == self.batch_size:
                        yield from batch
                        batch = []

                yield from batch
                f.seek(0)
