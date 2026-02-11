import math

import glfw

from mainrenderapi import Renderer, ConcreteWorldGen
from mathhelpers import get_camera_forward, get_camera_right
import numpy as np


def main():
    renderer = Renderer(1600, 1000, "Perlin World")

    worldgen = ConcreteWorldGen()
    world_w = 320
    world_d = 320
    height_scale = 120.0

    heights, world_w, world_d = worldgen.generate_world_heights(
        width=world_w,
        depth=world_d,
        noise_scale=0.0015,
        seed=1337,
    )

    vertices = []
    indices = []
    colors = []

    x_offset = -world_w / 2.0
    z_offset = -world_d / 2.0

    for z in range(world_d + 1):
        for x in range(world_w + 1):
            h = heights[z][x]
            y = (h - 0.45) * height_scale
            vertices.extend(
                [
                    x + x_offset,
                    y,
                    z + z_offset,
                ]
            )

    stride = world_w + 1
    ground_heights = []
    for z in range(world_d):
        row = []
        for x in range(world_w):
            i0 = z * stride + x
            i1 = i0 + 1
            i2 = i0 + stride
            i3 = i2 + 1

            indices.extend([i0, i1, i2])
            indices.extend([i1, i3, i2])

            h1 = heights[z][x]
            h2 = heights[z][x + 1]
            h3 = heights[z + 1][x]
            h4 = heights[z + 1][x + 1]
            row.append(h1)
            colors.append(worldgen.height_color((h1 + h2 + h3) / 3.0))
            colors.append(worldgen.height_color((h2 + h3 + h4) / 3.0))
        ground_heights.append(row)
    mesh = renderer.create_mesh(vertices, indices, colors)
    mesh.set_model_matrix(
        [
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
        ]
    )

    # Rotate the world 180 degrees around the Z axis (screen upside down).
    # mesh.set_model_matrix(
    #     [
    #         -1,
    #         0,
    #         0,
    #         0,
    #         0,
    #         -1,
    #         0,
    #         0,
    #         0,
    #         0,
    #         1,
    #         0,
    #         0,
    #         0,
    #         0,
    #         1,
    #     ]
    # )

    sample_height = worldgen.make_height_sampler(
        heights, world_w, world_d, height_scale
    )

    cursor_locked = True
    renderer.set_cursor_locked(cursor_locked)

    last_time = glfw.get_time()
    input_state = renderer.get_input()
    last_mouse = input_state.get_mouse_position()

    move_speed = 18.0
    mouse_sensitivity = 0.0025
    invert_mouse_y = False

    player_height = 1.8
    jump_speed = 9.0
    gravity = -22.0
    ground_snap = 0.15
    slope_limit_deg = 40.0
    max_climb = math.tan(math.radians(slope_limit_deg))

    vel_x = 0.0
    vel_y = 0.0
    vel_z = 0.0

    start_x = 0.0
    start_z = 0.0
    start_ground = sample_height(start_x, start_z)
    if start_ground is None:
        start_ground = 0.0
    renderer.set_camera_position(start_x, start_ground + player_height, start_z)
    renderer.set_camera_rotation(-0.35, 0.75)

    fps_accum = 0.0
    fps_frames = 0

    while not glfw.window_should_close(renderer.window):
        now = glfw.get_time()
        dt = now - last_time
        last_time = now

        input_state = renderer.get_input()

        if input_state.is_key_pressed(glfw.KEY_ESCAPE):
            cursor_locked = False
            renderer.set_cursor_locked(cursor_locked)
        if input_state.is_mouse_button_pressed(glfw.MOUSE_BUTTON_LEFT):
            cursor_locked = True
            renderer.set_cursor_locked(cursor_locked)

        mouse_x, mouse_y = input_state.get_mouse_position()
        if cursor_locked:
            dx = mouse_x - last_mouse[0]
            dy = mouse_y - last_mouse[1]
            pitch, yaw = renderer.get_camera_rotation()
            yaw += dx * mouse_sensitivity
            if invert_mouse_y:
                pitch += dy * mouse_sensitivity
            else:
                pitch -= dy * mouse_sensitivity
            pitch_clipped = np.clip(pitch, -1.57, 1.57)
            renderer.set_camera_rotation(pitch_clipped, yaw)
        last_mouse = (mouse_x, mouse_y)

        pitch, yaw = renderer.get_camera_rotation()
        forward = get_camera_forward(pitch, yaw)
        right = get_camera_right(pitch, yaw)

        move_x = 0.0
        move_z = 0.0

        if input_state.is_key_pressed(glfw.KEY_W):
            move_x -= forward[0]
            move_z -= forward[2]
        if input_state.is_key_pressed(glfw.KEY_S):
            move_x += forward[0]
            move_z += forward[2]
        if input_state.is_key_pressed(glfw.KEY_D):
            move_x += right[0]
            move_z += right[2]
        if input_state.is_key_pressed(glfw.KEY_A):
            move_x -= right[0]
            move_z -= right[2]
        length = math.sqrt(move_x * move_x + move_z * move_z)
        if length > 0.0001:
            move_x /= length
            move_z /= length

        cam_x, cam_y, cam_z = renderer.get_camera_position()

        # Desired horizontal velocity
        target_vx = move_x * move_speed
        target_vz = move_z * move_speed

        accel = 45.0
        friction = 16.0

        vel_x += (target_vx - vel_x) * min(1.0, accel * dt)
        vel_z += (target_vz - vel_z) * min(1.0, accel * dt)

        if length < 0.0001:
            vel_x *= max(0.0, 1.0 - friction * dt)
            vel_z *= max(0.0, 1.0 - friction * dt)

        # Gravity
        vel_y += gravity * dt

        # Predict next horizontal position
        next_x = cam_x + vel_x * dt
        next_z = cam_z + vel_z * dt

        ground_next = sample_height(next_x, next_z)
        ground_now = sample_height(cam_x, cam_z)

        if ground_next is None:
            next_x, next_z = cam_x, cam_z
            vel_x, vel_z = 0.0, 0.0
            ground_next = ground_now

        cam_x, cam_z = next_x, next_z

        # Simple ground collision: only keep player above the terrain.
        grounded = False
        if ground_next is not None:
            min_y = ground_next + player_height
            if cam_y <= min_y + ground_snap:
                cam_y = min_y
                if vel_y < 0:
                    vel_y = 0.0
                grounded = True
            if grounded and (
                input_state.is_key_pressed(glfw.KEY_SPACE)
                or glfw.get_key(renderer.window, glfw.KEY_SPACE) == glfw.PRESS
            ):
                vel_y += jump_speed * dt * -gravity
        cam_y = ground_heights[int(cam_z)][int(cam_x)] + player_height + vel_y
        renderer.set_camera_position(cam_x, cam_y, cam_z)

        renderer.run()

        fps_accum += dt
        fps_frames += 1
        if fps_accum >= 0.5:
            fps = fps_frames / fps_accum
            cam_x, cam_y, cam_z = renderer.get_camera_position()
            pitch, yaw = renderer.get_camera_rotation()
            pitch_deg = math.degrees(pitch)
            yaw_deg = math.degrees(yaw)
            glfw.set_window_title(
                renderer.window,
                f"Perlin World - {fps:.1f} FPS | "
                f"Pos x:{cam_x:.2f} y:{cam_y:.2f} z:{cam_z:.2f} | "
                f"Pitch:{pitch_deg:.1f} Yaw:{yaw_deg:.1f}",
            )
            fps_accum = 0.0
            fps_frames = 0


if __name__ == "__main__":
    main()
