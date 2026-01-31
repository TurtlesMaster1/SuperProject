import abc


class InputState(abc.ABC):
    @abc.abstractmethod
    def is_key_pressed(self, key):
        pass

    @abc.abstractmethod
    def get_mouse_position(self):
        pass

    @abc.abstractmethod
    def is_mouse_button_pressed(self, button):
        pass


class Mesh(abc.ABC):
    @abc.abstractmethod
    def set_model_matrix(self, mat4):
        pass

    @abc.abstractmethod
    def set_triangle_color(self, triangle_index, color):
        pass

    @abc.abstractmethod
    def draw(self):
        pass


class Renderer(abc.ABC):
    @abc.abstractmethod
    def create_mesh(self, vertices, indices, colors=None):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def run_frames(self, num_frames):
        pass

    @abc.abstractmethod
    def get_input(self):
        pass

    @abc.abstractmethod
    def set_camera_position(self, x, y, z):
        pass

    @abc.abstractmethod
    def get_camera_position(self):
        pass

    @abc.abstractmethod
    def set_camera_rotation(self, pitch, yaw):
        pass

    @abc.abstractmethod
    def get_camera_rotation(self):
        pass

    @abc.abstractmethod
    def set_cursor_locked(self, locked):
        pass