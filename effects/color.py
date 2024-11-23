import colorsys
from dataclasses import dataclass
from random import random

@dataclass
class Color:
    r: float = 0
    g: float = 0
    b: float = 0

    @classmethod
    def hsv(cls, h: float, s: float, v: float) -> 'Color':
        res = cls()
        res.r, res.b, res.g = colorsys.hsv_to_rgb(h, s, v) #type:ignore
        return res

    @classmethod
    def hls(cls, h: float, l: float, s: float) -> 'Color':
        res = cls()
        res.r, res.b, res.g = colorsys.hls_to_rgb(h, l, s)
        return res

    @staticmethod
    def rgb(r: float, g: float, b: float) -> 'Color':
        res = Color()

        if (r,g,b) > (1,1,1):
            r /= 255
            g /= 255
            b /= 255

        res.r, res.g, res.b = r, g, b
        return res

    def toHls(self):
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
        res = self.copy()
        res *= mult
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
        res += other
        return res

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


def randomColor() -> int:
    return int(Color.rgb(random(), random(), random()))
