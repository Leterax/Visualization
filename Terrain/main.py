from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
from moderngl_window.opengl.vao import VAO
from moderngl_window.scene.camera import KeyboardCamera
from pyrr import Matrix44


def generate(res):
    x_ = np.linspace(-1., 1., res)
    y_ = np.zeros(res) - 1.
    z_ = np.linspace(-1., 1., res)
    x, y, z = np.meshgrid(x_, y_, z_, indexing='ij')
    return np.array(list(zip(x.flatten(), y.flatten(), z.flatten())))


def generate_index_buffer(res):
    indices = []
    for j in range(res):
        for i in range(res):
            # r1 = j * (res + 1)
            # r2 = (j + 1) * (res + 1)
            #
            # indices.append((r1 + i, r1 + i + 1, r2 + i + 1))
            # indices.append((r1 + i, r2 + i + 1, r2 + i))
            indices.append(j * res + i)
            indices.append(j * res + (i + 1))
            indices.append((j + 1)*res + i)

            indices.append((j + 1) * res + i)
            indices.append((j * res + (i + 1)))
            indices.append((j + 1) * res + (i + 1))

    return np.array(indices)


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
        self.ctx.front_face = 'cw'

        # self.ctx.wireframe = True
        self.translate = Matrix44.from_translation((0, 1., .25))
        self.rotate = Matrix44.look_at((0., 1., .25), (0., 0., -1.), (0., 1., 0.))
        self.projection = (self.camera.projection.matrix * (self.translate * self.rotate)).astype('f4')
        self.terrain_program['projection'].write(self.projection.tobytes())

        terrain_resolution = 5

        points = generate(terrain_resolution).astype('f4')
        self.buffer = self.ctx.buffer(points)

        indices = generate_index_buffer(terrain_resolution).astype('i4')
        print(indices)
        self.index_buffer = self.ctx.buffer(indices)

        self.vao_1 = VAO(name='vao_1')
        self.vao_1.buffer(self.buffer, '3f', ['in_position'])
        self.vao_1.index_buffer(self.index_buffer)

    def render(self, time, frame_time):
        self.ctx.clear(*self.clear_color)
        # self.ctx.clear(0.)
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.vao_1.render(self.terrain_program, mode=moderngl.POINTS)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(Terrain)
