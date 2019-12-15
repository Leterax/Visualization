import math
from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
from moderngl_window import geometry
from moderngl_window.opengl.vao import VAO
from moderngl_window.scene.camera import KeyboardCamera
from pyrr import Matrix44


class Object:
    def __init__(self):
        self._scale = np.array((0., 0., 0.))
        self._rotation = np.array((0., 0., 0.))
        self._translation = np.array([0., 0., 0.])

        self._mt = np.eye(4)
        self._mr = np.eye(4)
        self._ms = np.eye(4)
        self.matrix = None

    # translation
    def set_translate(self, *xyz):
        self._translation = np.array(xyz).astype(float)
        self._mt = Matrix44.from_translation(self._translation)

    def translate(self, *xyz):
        self._translation += np.array(xyz).astype(float)
        self._mt = Matrix44.from_translation(self._translation)

    # rotation
    def set_rotation(self, *xyz):
        self._rotation = np.array(xyz).astype(float)
        self._mr = Matrix44.from_eulers(self._rotation)

    def rotate(self, *xyz):
        self._rotation += np.array(xyz).astype(float)
        self._mr = Matrix44.from_eulers(self._rotation)

    # scale
    def set_scale(self, *xyz):
        self._scale = np.array(xyz).astype(float)
        self._ms = Matrix44.from_scale(self._scale)

    def scale(self, *xyz):
        self._scale += np.array(xyz).astype(float)
        self._ms = Matrix44.from_scale(self._scale)

    def render(self, *args):
        raise NotImplemented()

    @property
    def matrix(self):
        return (self._mt * self._mr * self._ms).astype('f4')

    @matrix.setter
    def matrix(self, value):
        pass


class Cube(Object):
    def __init__(self, pos=(0, 0, 0), size=(1, 1, 1)):
        super().__init__()
        self._cube = geometry.cube(size=size, center=pos)

    def render(self, program):
        self._cube.render(program)


class Sphere(Object):
    def __init__(self, ctx, pos=(0, 0, 0), radius=1., size=(1, 1, 1), resolution=(36, 18)):
        super().__init__()
        self.set_translate(*pos)
        self.set_scale(*size)

        self.resolution = resolution
        self.radius = radius
        vertices, normals, tex = self.generate_vertices()

        self.buffer_vertices = ctx.ctx.buffer(np.array(vertices).flatten().astype('f4'))
        self.buffer_normals = ctx.ctx.buffer(np.array(normals).flatten().astype('f4'))
        self.buffer_tex = ctx.ctx.buffer(np.array(tex).flatten().astype('f4'))
        self.index_buffer = np.array(self.generate_indices()).astype('i4')
        self._sphere = VAO(name='_sphere')
        self._sphere.index_buffer(self.index_buffer)
        self._sphere.buffer(self.buffer_vertices, '3f', ['in_position'])
        self._sphere.buffer(self.buffer_normals, '3f', ['in_normal'])
        self._sphere.buffer(self.buffer_tex, '3f', ['in_tex'])

    def generate_vertices(self):
        sector_count = self.resolution[0]
        stack_count = self.resolution[1]
        sector_step = 2. * math.pi / sector_count
        stack_step = math.pi / stack_count

        inverted_len = 1. / self.radius

        vertices = []
        normals = []
        tex = []

        for i in range(stack_count + 1):
            stack_angle = math.pi / 2. - i * stack_step

            xy = self.radius * math.cos(stack_angle)
            z = self.radius * math.sin(stack_angle)

            for j in range(sector_count + 1):
                sector_angle = j * sector_step

                x = xy * math.cos(sector_angle)
                y = xy * math.sin(sector_angle)

                vertices.append((x, y, z))

                nx = x * inverted_len
                ny = y * inverted_len
                nz = z * inverted_len

                normals.append((nx, ny, nz))

                s = j / sector_count
                t = i / stack_count
                tex.append((s, t, 0))

        return vertices, normals, tex

    def generate_indices(self):
        sector_count = self.resolution[0]
        stack_count = self.resolution[1]

        indices = []

        for i in range(stack_count):
            k1 = i * (sector_count + 1)
            k2 = k1 + sector_count + 1

            for j in range(sector_count):

                if i != 0:
                    indices.append((k1, k2, k1 + 1))
                if i != (stack_count - 1):
                    indices.append((k1 + 1, k2, k2 + 1))
                k1 += 1
                k2 += 1

        return indices

    def render(self, program):
        self._sphere.render(program, mode=moderngl.LINES)


class CubeViz(mglw.WindowConfig):
    """Base class with built in 3D camera support"""
    title = "Cube"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = True
    samples = 16

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera.set_position(0, -4, 20)
        self.ctx.point_size = 2.
        self.render_program = self.load_program('.glsl')

        self.render_program['projection'].write(self.camera.projection.tobytes())
        self.render_program['m_camera'].write(self.camera.matrix.astype('f4').tobytes())

    def render(self, time, frame_time):
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.Jupiter.render(self.render_program)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(CubeViz)
