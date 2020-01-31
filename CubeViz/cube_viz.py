import math
from pathlib import Path
from typing import Tuple

import moderngl

import moderngl_window as mglw
from moderngl_window import geometry
from moderngl_window.scene.camera import KeyboardCamera

import numpy as np

from pyrr import Matrix44


class Object:
    def __init__(self) -> None:
        self._scale = np.array((0., 0., 0.))
        self._rotation = np.array((0., 0., 0.))
        self._translation = np.array((0., 0., 0.))

        self._mt = np.eye(4)
        self._mr = np.eye(4)
        self._ms = np.eye(4)
        self.matrix = None

    # translation
    def set_translate(self, *xyz: float) -> None:
        """Set the current translation by overwriting the old one."""
        self._translation = xyz
        self._mt = Matrix44.from_translation(self._translation)

    def translate(self, *xyz: float) -> None:
        """Translate by xyz."""
        self._translation += xyz
        self._mt = Matrix44.from_translation(self._translation)

    # rotation
    def set_rotation(self, *xyz: float) -> None:
        """Set the current rotation by overwriting the old one."""
        self._rotation = xyz
        self._mr = Matrix44.from_eulers(self._rotation)

    def rotate(self, *xyz: float) -> None:
        """Rotate by xyz."""
        self._rotation += xyz
        self._mr = Matrix44.from_eulers(self._rotation)

    # scale
    def set_scale(self, *xyz: float) -> None:
        """Set the current scale by overwriting the old one."""
        self._scale = xyz
        self._ms = Matrix44.from_scale(self._scale)

    def scale(self, *xyz: float) -> None:
        """Scale by xyz."""
        self._scale += xyz
        self._ms = Matrix44.from_scale(self._scale)

    def render(self, *args) -> None:
        raise NotImplementedError()

    @property
    def matrix(self) -> Matrix44:
        return (self._mt * self._mr * self._ms).astype('f4')

    @matrix.setter
    def matrix(self, value: Matrix44) -> None:
        pass


class Cube(Object):
    def __init__(self,
                 pos: Tuple[float, float, float] = (0, 0, 0),
                 size: Tuple[float, float, float] = (1, 1, 1)
                 ) -> None:
        super().__init__()
        self._cube = geometry.cube(size=size, center=pos)

    def render(self, program) -> None:
        self._cube.render(program)


class CubeViz(mglw.WindowConfig):
    """Base class with built in 3D camera support."""

    title = "Cube"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = True
    samples = 16

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.wnd.mouse_exclusivity = True
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = False
        self.render_program = self.load_program('my_shader.glsl')

        self.render_program['projection'].write(self.camera.projection.tobytes())
        self.render_program['m_camera'].write(self.camera.matrix.astype('f4').tobytes())
        self.cube = Cube(size=(.5, .5, .5))

    def render(self, time: float, frame_time: float) -> None:
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        s = math.sin(time * 2) / 2 + 1.5

        self.cube.set_rotation(time, time / 2, time / 3)
        self.cube.set_translate(s * 4 - 6, 0, -3.0)

        self.render_program['model'].write(self.cube.matrix)
        self.render_program['m_camera'].write(self.camera.matrix.astype('f4'))
        self.cube.render(self.render_program)

    def resize(self, width: int, height: int) -> None:
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(CubeViz)
