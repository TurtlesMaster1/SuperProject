#from api_defs import Mesh, Renderer, InputState
from renderer_impl import ConcreteMesh, ConcreteRenderer, ConcreteInputState

# Expose concrete implementations as the API
Mesh = ConcreteMesh
Renderer = ConcreteRenderer
InputState = ConcreteInputState
