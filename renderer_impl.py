import glfw
import moderngl
import struct
import math
import time
from mathhelpers import perspective, rotation_y, translate, mat4_mul
from api_defs import Mesh, Renderer


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
    def __init__(self, width=800, height=600, title="Renderer"):
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
        self.ctx.clear(0.1, 0.1, 1)
        self.ctx.enable(moderngl.DEPTH_TEST)

        t = time.time() - self.start_time

        proj = perspective(math.radians(60.0), self.width / self.height, 0.1, 100.0)
        view = translate(-3.0)

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