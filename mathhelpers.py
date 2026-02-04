
import math

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(a, b, t):
    return a + t * (b - a)


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

def rotation_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        1, 0, 0, 0,
        0, c, -s, 0,
        0, s, c, 0,
        0, 0, 0, 1,
    ]

def translate(x, y=0, z=0):
    return [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        x, y, z, 1,
    ]

def mat4_mul(a, b):
    return [
        sum(a[row + i * 4] * b[col * 4 + i] for i in range(4))
        for col in range(4)
        for row in range(4)
    ]

def get_camera_forward(pitch, yaw):
    """Get forward direction vector from pitch and yaw angles."""
    return (
        math.sin(yaw),
        math.sin(pitch),
        math.cos(yaw)
    )

def get_camera_right(pitch, yaw):
    """Get right direction vector from pitch and yaw angles."""
    return (
        -math.cos(yaw),
        0,
        math.sin(yaw)
    )
