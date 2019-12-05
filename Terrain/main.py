from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
from moderngl_window.opengl.vao import VAO
from moderngl_window.scene.camera import KeyboardCamera


def generate(res):
    x_ = np.linspace(-1., 1., res)
    y_ = np.linspace(-1., 1., res)
    z_ = np.zeros(res)
    x, y, z = np.meshgrid(x_, y_, z_, indexing='ij')
    return np.array(list(zip(x.flatten(), y.flatten(), z.flatten())))


class Terrain(mglw.WindowConfig):
    """"""
    title = "Terrain"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = True
    samples = 16

    clear_color = (51 / 255, 51 / 255, 51 / 255)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.terrain_program = self.load_program('my_shader.glsl')

        # self.ctx.wireframe = True

        self.terrain_program['projection'].write(self.camera.projection.tobytes())

        terrain_resolution = 5

        points = generate(terrain_resolution)
        self.buffer = self.ctx.buffer(points)

        self.vao = VAO(name='vao_1')
        self.vao.buffer(self.buffer, '3f', ['in_position'])

    def render(self, time, frame_time):
        # self.ctx.clear(*self.clear_color)
        self.ctx.clear(1, 1, 1)
        self.vao.render(self.terrain_program, mode=moderngl.POINTS)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(Terrain)
