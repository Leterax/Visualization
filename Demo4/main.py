import math
from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
from moderngl_window import geometry
from moderngl_window.scene.camera import KeyboardCamera
from pyrr import Matrix44


class Object:
    def __init__(self):
        self._scale = np.array((0., 0., 0.))
        self._rotation = np.array((0., 0., 0.))
        self._translation = np.array((0., 0., 0.))

        self._mt = np.eye(4)
        self._mr = np.eye(4)
        self._ms = np.eye(4)
        self.matrix = None

    # translation
    def set_translate(self, *xyz):
        self._translation = xyz
        self._mt = Matrix44.from_translation(self._translation)

    def translate(self, *xyz):
        self._translation += xyz
        self._mt = Matrix44.from_translation(self._translation)

    # rotation
    def set_rotation(self, *xyz):
        self._rotation = xyz
        self._mr = Matrix44.from_eulers(self._rotation)

    def rotate(self, *xyz):
        self._rotation += xyz
        self._mr = Matrix44.from_eulers(self._rotation)

    # scale
    def set_scale(self, *xyz):
        self._scale = xyz
        self._ms = Matrix44.from_scale(self._scale)

    def scale(self, *xyz):
        self._scale += xyz
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


class DroneViz(mglw.WindowConfig):
    """Base class with built in 3D camera support"""
    title = "DroneViz"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = True
    samples = 16

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.mouse_exclusivity = True
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = False
        self.render_program = self.load_program('my_shader.glsl')

        self.render_program['projection'].write(self.camera.projection.tobytes())
        self.render_program['m_camera'].write(self.camera.matrix.astype('f4').tobytes())
        self.cube = Cube(size=(.5, .5, .5))
        
    def render(self, time, frame_time):
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        # self.render_program['time'].value = min(time / 1, 1.0)

        s = math.sin(time * 2) / 2 + 1.5

        self.cube.set_rotation(time, time / 2, time / 3)
        self.cube.set_translate(s * 4 - 6, 0, -3.0)

        self.render_program['model'].write(self.cube.matrix)
        self.render_program['m_camera'].write(self.camera.matrix.astype('f4'))
        self.cube.render(self.render_program)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if self.camera_enabled:
            self.camera.key_input(key, action, modifiers)

        if action == keys.ACTION_PRESS:
            if key == keys.C:
                self.camera_enabled = not self.camera_enabled
                self.wnd.mouse_exclusivity = self.camera_enabled
                self.wnd.cursor = not self.camera_enabled
            if key == keys.SPACE:
                self.timer.toggle_pause()

    def mouse_position_event(self, x: int, y: int, dx, dy):
        if self.camera_enabled:
            self.camera.rot_state(-dx, -dy)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(DroneViz)
