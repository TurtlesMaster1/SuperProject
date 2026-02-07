import math
import random

from mathhelpers import fade, lerp


def _grad(hash_value, x, y):
    h = hash_value & 3
    u = x if h < 2 else y
    v = y if h < 2 else x
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)


def build_permutation(seed):
    rng = random.Random(seed)
    p = list(range(256))
    rng.shuffle(p)
    return p + p


def perlin2d(x, y, perm):
    xi = math.floor(x) & 255
    yi = math.floor(y) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)

    u = fade(xf)
    v = fade(yf)

    aa = perm[perm[xi] + yi]
    ab = perm[perm[xi] + yi + 1]
    ba = perm[perm[xi + 1] + yi]
    bb = perm[perm[xi + 1] + yi + 1]

    x1 = lerp(_grad(aa, xf, yf), _grad(ba, xf - 1, yf), u)
    x2 = lerp(_grad(ab, xf, yf - 1), _grad(bb, xf - 1, yf - 1), u)

    return lerp(x1, x2, v)


def fbm(x, y, perm, octaves=5, lacunarity=2.0, gain=0.5):
    amplitude = 1.0
    frequency = 1.0
    total = 0.0
    norm = 0.0
    for _ in range(octaves):
        total += perlin2d(x * frequency, y * frequency, perm) * amplitude
        norm += amplitude
        amplitude *= gain
        frequency *= lacunarity
    return total / norm if norm else 0.0


def height_color(height_value):
    if height_value < 0.38:
        return (0.08, 0.28, 0.65)
    if height_value < 0.45:
        return (0.72, 0.66, 0.46)
    if height_value < 0.82:
        return (0.10, 0.62, 0.16)
    if height_value < 0.92:
        return (0.40, 0.40, 0.42)
    return (0.92, 0.92, 0.95)


def generate_world_heights(width=120, depth=120, noise_scale=0.06, seed=1337):
    perm = build_permutation(seed)
    heights = []

    for z in range(depth + 1):
        row = []
        for x in range(width + 1):
            nx = x * noise_scale
            nz = z * noise_scale
            h = fbm(nx, nz, perm)
            h = (h + 1.0) * 0.5
            h = h**2
            h += 0.5
            row.append(h)
        heights.append(row)

    return heights, width, depth


def maked_height_sampler(heights, width, depth, height_scale):
    def sample_height(x, z):
        gx = x + width / 2.0
        gz = z + depth / 2.0

        if gx < 0 or gz < 0 or gx > width or gz > depth:
            return None

        x0 = int(math.floor(gx))
        z0 = int(math.floor(gz))
        x1 = min(x0 + 1, width)
        z1 = min(z0 + 1, depth)

        fx = gx - x0
        fz = gz - z0

        h00 = heights[z0][x0]
        h10 = heights[z0][x1]
        h01 = heights[z1][x0]
        h11 = heights[z1][x1]

        h0 = h00 + (h10 - h00) * fx
        h1 = h01 + (h11 - h01) * fx
        h = h0 + (h1 - h0) * fz

        return (h - 0.45) * height_scale

    return sample_height


class ConcreteWorldGen:
    def build_permutation(self, seed):
        return build_permutation(seed)

    def perlin2d(self, x, y, perm):
        return perlin2d(x, y, perm)

    def fbm(self, x, y, perm, octaves=5, lacunarity=2.0, gain=0.5):
        return fbm(x, y, perm, octaves=octaves, lacunarity=lacunarity, gain=gain)

    def height_color(self, height_value):
        return height_color(height_value)

    def generate_world_heights(self, width=120, depth=120, noise_scale=0.06, seed=1337):
        return generate_world_heights(
            width=width, depth=depth, noise_scale=noise_scale, seed=seed
        )

    def make_height_sampler(self, heights, width, depth, height_scale):
        return maked_height_sampler(heights, width, depth, height_scale)
