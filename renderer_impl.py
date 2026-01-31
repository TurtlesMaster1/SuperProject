import glfw
import moderngl
import struct
import math
import time
from mathhelpers import perspective, rotation_y, rotation_x, translate, mat4_mul
from api_defs import Mesh, Renderer, InputState


class ConcreteInputState(InputState):
    def __init__(self, window):
        self.window = window
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons_pressed = set()
        
        # Set up callbacks
        glfw.set_key_callback(window, self._key_callback)
        glfw.set_mouse_button_callback(window, self._mouse_button_callback)
        glfw.set_cursor_pos_callback(window, self._cursor_pos_callback)
    
    def _key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.keys_pressed.add(key)
        elif action == glfw.RELEASE:
            self.keys_pressed.discard(key)
    
    def _mouse_button_callback(self, window, button, action, mods):
        if action == glfw.PRESS:
            self.mouse_buttons_pressed.add(button)
        elif action == glfw.RELEASE:
            self.mouse_buttons_pressed.discard(button)
    
    def _cursor_pos_callback(self, window, xpos, ypos):
        self.mouse_pos = (xpos, ypos)
    
    def is_key_pressed(self, key):
        return key in self.keys_pressed
    
    def get_mouse_position(self):
        return self.mouse_pos
    
    def is_mouse_button_pressed(self, button):
        return button in self.mouse_buttons_pressed


class ConcreteMesh(Mesh):
    def __init__(self, ctx, program, vertices, indices, colors=None):
        self.program = program
        self.vbo = ctx.buffer(struct.pack(f"{len(vertices)}f", *vertices))
        self.ibo = ctx.buffer(struct.pack(f"{len(indices)}I", *indices))

        self.vao = ctx.vertex_array(
            program,
            [
                (self.vbo, "3f", "in_pos"),
            ],
            self.ibo,
        )

        num_triangles = len(indices) // 3
        if colors is None:
            self.colors = [(1.0, 1.0, 1.0)] * num_triangles
        else:
            self.colors = colors

        self.model_matrix = None

    def set_model_matrix(self, mat4):
        self.model_matrix = mat4

    def set_triangle_color(self, triangle_index, color):
        self.colors[triangle_index] = color

    def draw(self):
        for i, color in enumerate(self.colors):
            self.program["color"].write(struct.pack("3f", *color))
            self.vao.render(moderngl.TRIANGLES, first=i*3, vertices=3)


class ConcreteRenderer(Renderer):
    def __init__(self, width=1800, height=1200, title="Renderer"):
        if not glfw.init():
            raise RuntimeError("GLFW init failed")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            raise RuntimeError("Window creation failed")

        glfw.make_context_current(self.window)

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.program = self._create_program()
        self.meshes = []

        self.width = width
        self.height = height
        self.start_time = time.time()
        
        # Initialize input state
        self.input_state = ConcreteInputState(self.window)
        
        # Initialize camera position
        self.camera_pos = (-3.0, -20, 0.0)
        
        # Initialize camera rotation (pitch, yaw)
        self.camera_rotation = (0.0, 0.0)
        self.last_mouse_pos = (0, 0)
        self.cursor_locked = False
        self.center_x = width // 2
        self.center_y = height // 2

    def _create_program(self):
        return self.ctx.program(
            vertex_shader="""
            #version 330
            in vec3 in_pos;
            uniform mat4 mvp;

            void main() {
                gl_Position = mvp * vec4(in_pos, 1.0);
            }
            """,
            fragment_shader="""
#version 330

uniform vec3 color;   // <-- use this to set the triangle color
out vec4 fragColor;   // <-- different name than the uniform

void main() {
    fragColor = vec4(color, 1.0);
}
"""
        )

    def create_mesh(self, vertices, indices, colors=None):
        mesh = ConcreteMesh(self.ctx, self.program, vertices, indices, colors)
        self.meshes.append(mesh)
        return mesh

    def run(self):
        if glfw.window_should_close(self.window):
            glfw.terminate()
            return
        self._render_frame()
        # Present the rendered frame and process events so an interactive
        # `run()` loop actually updates the window. `run_frames` already
        # does swap/poll, but `run()` did not — causing the window to stay
        # un-updated when used from `main.py`.
        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def _render_frame(self):
        self.ctx.clear(148/255.0, 189/255.0, 255/255.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        t = self.start_time

        proj = perspective(math.radians(60.0), self.width / self.height, 0.1, 100.0)
        
        # Apply camera rotation then translation
        pitch, yaw = self.camera_rotation
        rot_x = rotation_x(pitch)
        rot_y = rotation_y(yaw)
        view = mat4_mul(rot_x, mat4_mul(rot_y, translate(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2])))

        for mesh in self.meshes:
            model = mesh.model_matrix or rotation_y(t)
            mvp = mat4_mul(proj, mat4_mul(view, model))
            self.program["mvp"].write(struct.pack("16f", *mvp))
            mesh.draw()

    def run_frames(self, num_frames):
        import time
        start = time.time()
        for _ in range(num_frames):
            if glfw.window_should_close(self.window):
                break
            self._render_frame()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        end = time.time()
        fps = num_frames / (end - start) if end > start else 0
        return fps

    def get_input(self):
        return self.input_state

    def set_camera_position(self, x, y, z):
        self.camera_pos = (x, y, z)

    def get_camera_position(self):
        return self.camera_pos

    def set_camera_rotation(self, pitch, yaw):
        self.camera_rotation = (pitch, yaw)

    def get_camera_rotation(self):
        return self.camera_rotation

    def set_cursor_locked(self, locked):
        self.cursor_locked = locked
        if locked:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        else:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)