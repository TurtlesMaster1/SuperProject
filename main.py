from mainrenderapi import Renderer
from mathhelpers import rotation_y
import time

renderer = Renderer()

# Square mesh
vertices = [
    -0.5, -0.5, 0.0,
     0.5, -0.5, 0.0,
     0.5,  0.5, 0.0,
    -0.5,  0.5, 0.0,
    1.0, 1.0, 1.0,  # Extra vertex to demonstrate flexibility
]

indices = [
    0, 1, 4,
    1, 2, 4,
    2, 3, 4,
    3, 0, 4,
]



mesh = renderer.create_mesh(vertices, indices)
while True:
    mesh.set_model_matrix(rotation_y(time.time()))

    renderer.run()