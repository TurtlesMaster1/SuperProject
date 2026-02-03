import math
import random

import glfw

from mainrenderapi import Renderer
from mathhelpers import get_camera_forward, get_camera_right


def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a, b, t):
    return a + t * (b - a)


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

    u = _fade(xf)
    v = _fade(yf)

    aa = perm[perm[xi] + yi]
    ab = perm[perm[xi] + yi + 1]
    ba = perm[perm[xi + 1] + yi]
    bb = perm[perm[xi + 1] + yi + 1]

    x1 = _lerp(_grad(aa, xf, yf), _grad(ba, xf - 1, yf), u)
    x2 = _lerp(_grad(ab, xf, yf - 1), _grad(bb, xf - 1, yf - 1), u)

    return _lerp(x1, x2, v)


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
    if height_value < 0.42:
        return (0.08, 0.28, 0.65)
    if height_value < 0.48:
        return (0.72, 0.66, 0.46)
    if height_value < 0.70:
        return (0.12, 0.55, 0.18)
    if height_value < 0.85:
        return (0.40, 0.40, 0.42)
    return (0.92, 0.92, 0.95)


def generate_world_mesh(renderer, width=120, depth=120, noise_scale=0.06, height_scale=14.0, seed=1337):
    perm = build_permutation(seed)
    vertices = []
    indices = []
    colors = []
    heights = []

    x_offset = -width / 2.0
    z_offset = -depth / 2.0

    for z in range(depth + 1):
        for x in range(width + 1):
            nx = x * noise_scale
            nz = z * noise_scale
            h = fbm(nx, nz, perm)
            h = (h + 1.0) * 0.5
            h = h ** 2
            h+=0.5
            heights.append(h)
            y = (h - 0.45) * height_scale
            vertices.extend([
                x + x_offset,
                y,
                z + z_offset,
            ])

    stride = width + 1
    for z in range(depth):
        for x in range(width):
            i0 = z * stride + x
            i1 = i0 + 1
            i2 = i0 + stride
            i3 = i2 + 1

            indices.extend([i0, i1, i2])
            indices.extend([i1, i3, i2])

            h1 = heights[i0]
            h2 = heights[i1]
            h3 = heights[i2]
            h4 = heights[i3]

            colors.append(height_color((h1 + h2 + h3) / 3.0))
            colors.append(height_color((h2 + h3 + h4) / 3.0))

    mesh = renderer.create_mesh(vertices, indices, colors)
    mesh.set_model_matrix([
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1,
    ])
    return mesh


def main():
    renderer = Renderer(1600, 1000, "Perlin World")

    generate_world_mesh(renderer)

    renderer.set_camera_position(0.0, -10.0, -40.0)
    renderer.set_camera_rotation(0.35, 0.75)

    cursor_locked = True
    renderer.set_cursor_locked(cursor_locked)

    last_time = glfw.get_time()
    last_mouse = glfw.get_cursor_pos(renderer.window)

    move_speed = 18.0
    mouse_sensitivity = 0.0025

    fps_accum = 0.0
    fps_frames = 0

    while not glfw.window_should_close(renderer.window):
        now = glfw.get_time()
        dt = now - last_time
        last_time = now

        if glfw.get_key(renderer.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            cursor_locked = False
            renderer.set_cursor_locked(cursor_locked)
        if glfw.get_mouse_button(renderer.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            cursor_locked = True
            renderer.set_cursor_locked(cursor_locked)

        mouse_x, mouse_y = glfw.get_cursor_pos(renderer.window)
        if cursor_locked:
            dx = mouse_x - last_mouse[0]
            dy = mouse_y - last_mouse[1]
            pitch, yaw = renderer.get_camera_rotation()
            yaw += dx * mouse_sensitivity
            pitch -= dy * mouse_sensitivity
            pitch = max(-1.5, min(1.5, pitch))
            renderer.set_camera_rotation(pitch, yaw)
        last_mouse = (mouse_x, mouse_y)

        pitch, yaw = renderer.get_camera_rotation()
        forward = get_camera_forward(pitch, yaw)
        right = get_camera_right(pitch, yaw)

        move_x = 0.0
        move_y = 0.0
        move_z = 0.0

        if glfw.get_key(renderer.window, glfw.KEY_W) == glfw.PRESS:
            move_x += forward[0]
            move_y += forward[1]
            move_z += forward[2]
        if glfw.get_key(renderer.window, glfw.KEY_S) == glfw.PRESS:
            move_x -= forward[0]
            move_y -= forward[1]
            move_z -= forward[2]
        if glfw.get_key(renderer.window, glfw.KEY_D) == glfw.PRESS:
            move_x += right[0]
            move_z += right[2]
        if glfw.get_key(renderer.window, glfw.KEY_A) == glfw.PRESS:
            move_x -= right[0]
            move_z -= right[2]
        if glfw.get_key(renderer.window, glfw.KEY_SPACE) == glfw.PRESS:
            move_y += 1.0
        if glfw.get_key(renderer.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            move_y -= 1.0

        length = math.sqrt(move_x * move_x + move_y * move_y + move_z * move_z)
        if length > 0.0001:
            move_x /= length
            move_y /= length
            move_z /= length

        cam_x, cam_y, cam_z = renderer.get_camera_position()
        cam_x += move_x * move_speed * dt
        cam_y += move_y * move_speed * dt
        cam_z += move_z * move_speed * dt
        renderer.set_camera_position(cam_x, cam_y, cam_z)

        renderer.run()

        fps_accum += dt
        fps_frames += 1
        if fps_accum >= 0.5:
            fps = fps_frames / fps_accum
            glfw.set_window_title(renderer.window, f"Perlin World - {fps:.1f} FPS")
            fps_accum = 0.0
            fps_frames = 0


if __name__ == "__main__":
    main()
