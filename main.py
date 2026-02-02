from mainrenderapi import Renderer
from mathhelpers import get_camera_forward, get_camera_right
from math import floor
import time
import random
import glfw

# =========================
# Renderer init
# =========================
print("[1/6] Initializing renderer...")
renderer = Renderer()
print("[2/6] Renderer initialized successfully")

# =========================
# Constants
# =========================
BLOCK_HALF = 0.5
PLAYER_RADIUS = 3
PLAYER_HEIGHT = 18
GRAVITY = -2
JUMP_VELOCITY = 0.35
CAMERA_SPEED = 0.5
MOUSE_SENS = 0.05
EYE_HEIGHT = 1.6

# =========================
# Cube helpers
# =========================
def create_cube_vertices(x, y, z, size=0.5):
    s = size
    return [
        x-s, y-s, z+s,  x+s, y-s, z+s,  x+s, y+s, z+s,  x-s, y+s, z+s,
        x-s, y-s, z-s,  x-s, y+s, z-s,  x+s, y+s, z-s,  x+s, y-s, z-s,
        x-s, y+s, z-s,  x-s, y+s, z+s,  x+s, y+s, z+s,  x+s, y+s, z-s,
        x-s, y-s, z-s,  x+s, y-s, z-s,  x+s, y-s, z+s,  x-s, y-s, z+s,
        x+s, y-s, z-s,  x+s, y+s, z-s,  x+s, y+s, z+s,  x+s, y-s, z+s,
        x-s, y-s, z-s,  x-s, y-s, z+s,  x-s, y+s, z+s,  x-s, y+s, z-s,
    ]

def create_cube_indices():
    idx = []
    for f in range(6):
        b = f * 4
        idx += [b, b+1, b+2, b, b+2, b+3]
    return idx

# =========================
# Terrain generation
# =========================
def generate_terrain(w, h, cx, cz, mh):
    blocks = []
    for x in range(-w//2, w//2):
        for z in range(-h//2, h//2):
            dx = x - cx
            dz = z - cz
            dist = (dx*dx + dz*dz) ** 0.5
            falloff = max(0, mh - dist * 0.1)

            blocks.append((x, -1, z))  # ground
            for y in range(int(falloff)):
                blocks.append((x, y, z))
    return blocks

print("[3/6] Generating terrain...")
block_positions = generate_terrain(16, 16, 0, 0, 8)
print(f"[4/6] Generated {len(block_positions)} blocks")

# =========================
# Mesh creation
# =========================
meshes = []
indices = create_cube_indices()

for x, y, z in block_positions:
    verts = create_cube_vertices(x, y, z)
    mesh = renderer.create_mesh(verts, indices)
    for i in range(12):
        mesh.set_triangle_color(i, (random.random(), random.random(), random.random()))
    meshes.append(mesh)

print("[5/6] Meshes created")

# =========================
# Block set (FIXED for negatives)
# =========================
block_set = set()
for x, y, z in block_positions:
    block_set.add((floor(x), floor(y), floor(z)))

# =========================
# Collision
# =========================
def collides(px, py, pz):
    min_x = floor(px - PLAYER_RADIUS)
    max_x = floor(px + PLAYER_RADIUS)
    min_y = floor(py)
    max_y = floor(py + PLAYER_HEIGHT)
    min_z = floor(pz - PLAYER_RADIUS)
    max_z = floor(pz + PLAYER_RADIUS)

    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            for z in range(min_z, max_z + 1):
                if (x, y, z) in block_set:
                    return True
    return False

def move_axis(px, py, pz, dx, dy, dz):
    grounded = False

    if dx != 0 and not collides(px + dx, py, pz):
        px += dx

    if dz != 0 and not collides(px, py, pz + dz):
        pz += dz

    if dy != 0:
        if not collides(px, py + dy, pz):
            py += dy
        else:
            if dy < 0:
                grounded = True

    return px, py, pz, grounded

# =========================
# Input / camera
# =========================
renderer.set_cursor_locked(True)
velocity_y = 0.0
on_ground = False
last_mouse = None

print("[6/6] Starting main loop")

while True:
    inp = renderer.get_input()
    cam_x, cam_y, cam_z = renderer.get_camera_position()
    pitch, yaw = renderer.get_camera_rotation()

    forward = get_camera_forward(pitch, yaw)
    right = get_camera_right(pitch, yaw)

    dx = dz = 0.0
    if inp.is_key_pressed(glfw.KEY_W):
        dx += forward[0] * CAMERA_SPEED
        dz += forward[2] * CAMERA_SPEED
    if inp.is_key_pressed(glfw.KEY_S):
        dx -= forward[0] * CAMERA_SPEED
        dz -= forward[2] * CAMERA_SPEED
    if inp.is_key_pressed(glfw.KEY_A):
        dx -= right[0] * CAMERA_SPEED
        dz -= right[2] * CAMERA_SPEED
    if inp.is_key_pressed(glfw.KEY_D):
        dx += right[0] * CAMERA_SPEED
        dz += right[2] * CAMERA_SPEED
    if inp.is_key_pressed(glfw.KEY_ESCAPE):
        renderer.set_cursor_locked(False)

    velocity_y += GRAVITY
    dy = velocity_y

    if inp.is_key_pressed(glfw.KEY_SPACE) and on_ground:
        velocity_y = JUMP_VELOCITY
        dy = velocity_y
        on_ground = False

    # use feet position for collision
    cam_x, cam_y, cam_z, grounded = move_axis(
        cam_x, cam_y - EYE_HEIGHT, cam_z, dx, dy, dz
    )

    cam_y += EYE_HEIGHT
    on_ground = grounded
    if grounded:
        velocity_y = 0.0

    mx, my = inp.get_mouse_position()
    if last_mouse:
        yaw -= (mx - last_mouse[0]) * MOUSE_SENS
        pitch -= (my - last_mouse[1]) * MOUSE_SENS
    last_mouse = (mx, my)

    renderer.set_camera_position(cam_x, cam_y, cam_z)
    renderer.set_camera_rotation(pitch, yaw)
    renderer.run()

