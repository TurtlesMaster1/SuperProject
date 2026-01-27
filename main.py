from mainrenderapi import Renderer
from mathhelpers import rotation_y
import time

renderer = Renderer()

vertices = [
    -1.0, -1.0, 0.0,   # bottom-left
     1.0, -1.0, 0.0,   # bottom-right
     1.0,  1.0, 0.0,   # top-right
    -1.0,  1.0, 0.0,   # top-left
]

indices = [
    0, 1, 2,
    2, 3, 0,
]

mesh = renderer.create_mesh(vertices, indices)

# Triangle 0 = ground
mesh.set_triangle_color(0, (0.0, 0.6, 0.0))   # green ground

# Triangle 1 = sky
mesh.set_triangle_color(1, (0.2, 0.6, 1.0))   # blue sky

while True:
    mesh.set_model_matrix(rotation_y(time.time()))

    renderer.run()