
import math


def perspective(fovy, aspect, near, far):
    f = 1.0 / math.tan(fovy / 2.0)
    return [
        f / aspect, 0, 0, 0,
        0, f, 0, 0,
        0, 0, (far + near) / (near - far), -1,
        0, 0, (2 * far * near) / (near - far), 0,
    ]

def rotation_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [
         c, 0, s, 0,
         0, 1, 0, 0,
        -s, 0, c, 0,
         0, 0, 0, 1,
    ]

def translate(z):
    return [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, z, 1,
    ]

def mat4_mul(a, b):
    return [
        sum(a[row + i * 4] * b[col * 4 + i] for i in range(4))
        for col in range(4)
        for row in range(4)
    ]