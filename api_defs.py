import abc


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