from api_defs import Mesh, Renderer
from renderer_impl import ConcreteMesh, ConcreteRenderer

# Expose concrete implementations as the API
Mesh = ConcreteMesh
Renderer = ConcreteRenderer
