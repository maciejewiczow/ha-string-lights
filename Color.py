import colorsys

class Color:
    @classmethod
    def hsv(cls, h: float, s: float, v: float) -> 'Color':
        res = cls()
        res.r, res.b, res.g = colorsys.hsv_to_rgb(h, s, v)
        return res

    @classmethod
    def hls(cls, h: float, l: float, s: float) -> 'Color':
        res = cls()
        res.r, res.b, res.g = colorsys.hls_to_rgb(h, l, s)
        return res

    @classmethod
    def rgb(cls, r: float, g: float, b: float) -> 'Color':
        res = cls()

        r /= 255
        g /= 255
        b /= 255

        res.r, res.g, res.b = r, g, b
        return res

    def __init__(self, r = 1, g = 1, b = 1) -> None:
        self.r = r
        self.g = g
        self.b = b

    def __iter__(self):
        yield 'r', self.r*255
        yield 'g', self.g*255
        yield 'b', self.b*255

    @classmethod
    def from_dict(cls, dict: dict) -> 'Color':
        return cls().rgb(dict['r'], dict['g'], dict['b'])

    def to_tuple(self):
        return int(self.r*255), int(self.g*255), int(self.b*255)

    def to_hls(self):
        return colorsys.rgb_to_hls(self.r, self.g, self.b)

    def copy(self) -> 'Color':
        res = Color()
        res.r, res.g, res.b = self.r, self.g, self.b
        return res

    def __int__(self):
        return (int(self.r*255) << 16) | (int(self.g*255) << 8) | int(self.b*255)

    def __imul__(self, mult: float):
        if (mult > 1):
            mult = 1

        self.r *= mult
        self.g *= mult
        self.b *= mult

        return self

    def __mul__(self, mult: float) -> 'Color':
        if (mult > 1):
            mult = 1

        res = self.copy()

        res.r *= mult
        res.g *= mult
        res.b *= mult

        return res

    def __iadd__(self, other: 'Color'):
        self.r += other.r
        self.g += other.g
        self.b += other.b

        if self.r > 1:
            self.r = 1

        if self.g > 1:
            self.g = 1

        if self.b > 1:
            self.b = 1

        return self

    def __add__(self, other: 'Color') -> 'Color':
        res = self.copy()

        res.r += other.r
        res.g += other.g
        res.b += other.b

        if res.r > 1:
            res.r = 1

        if res.g > 1:
            res.g = 1

        if res.b > 1:
            res.b = 1

        return res

    def __eq__(self, other: 'Color') -> bool:
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __str__(self):
        return "#{:x}".format(int(self)).lower()

    def __repr__(self):
        return str(self)

    def lightness(self, l: float):
        res = self.copy()

        h, _, s = colorsys.rgb_to_hls(self.r, self.g, self.b)
        res.r, res.g, res.b = colorsys.hls_to_rgb(h, l, s)

        return res

    def hue(self, h: float):
        res = self.copy()

        _, l, s = colorsys.rgb_to_hls(self.r, self.g, self.b)
        res.r, res.g, res.b = colorsys.hls_to_rgb(h, l, s)

        return res

    def blend(self, other: 'Color', fraction: float) -> 'Color':
        return self*(1-fraction) + other*fraction
