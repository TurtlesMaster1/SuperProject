from mainrenderapi import Renderer
from mathhelpers import rotation_y

renderer = Renderer()

# Square mesh
vertices = [
    -0.5, -0.5, 0.0,
     0.5, -0.5, 0.0,
     0.5,  0.5, 0.0,
    -0.5,  0.5, 0.0,
]

indices = [
    0, 1, 2,
    2, 3, 0,
]

mesh = renderer.create_mesh(vertices, indices)
mesh.set_model_matrix(rotation_y(0.5))

renderer.run()
