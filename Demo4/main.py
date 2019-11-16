from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
from moderngl_window import geometry
from moderngl_window.scene.camera import KeyboardCamera

CUBE_VERTICES = np.array([
    # front
    -1.0, -1.0, 1.0,
    1.0, -1.0, 1.0,
    1.0, 1.0, 1.0,
    -1.0, 1.0, 1.0,
    # back
    -1.0, -1.0, -1.0,
    1.0, -1.0, -1.0,
    1.0, 1.0, -1.0,
    -1.0, 1.0, -1.0
])


class ModelMatrix:
    def __init__(self):
        self._translation_matrix = np.eye(4)

        self._scaling_matrix = np.eye(4)

        self._rotation_matrix_x = np.eye(4)
        self._rotation_matrix_y = np.eye(4)
        self._rotation_matrix_z = np.eye(4)

        self._rotations = (self._rotate_x, self._rotate_y, self._rotate_z)

    def translate(self, *xyz):
        self._translation_matrix[-1, 0] = xyz[0]
        self._translation_matrix[-1, 1] = xyz[1]
        self._translation_matrix[-1, 2] = xyz[2]

    def scale(self, *xyz):
        self._scaling_matrix[0, 0] = xyz[0]
        self._scaling_matrix[1, 1] = xyz[1]
        self._scaling_matrix[2, 2] = xyz[2]

    def rotate(self, theta, axis=0):
        self._rotations[axis](theta)

    # axis rotation functions #

    def _rotate_x(self, theta):
        self._rotation_matrix_x[1, 1] = np.cos(theta)
        self._rotation_matrix_x[1, 2] = -np.sin(theta)
        self._rotation_matrix_x[2, 1] = np.sin(theta)
        self._rotation_matrix_x[2, 2] = np.cos(theta)

    def _rotate_y(self, theta):
        self._rotation_matrix_y[0, 0] = np.cos(theta)
        self._rotation_matrix_y[2, 0] = -np.sin(theta)
        self._rotation_matrix_y[0, 2] = np.sin(theta)
        self._rotation_matrix_y[2, 2] = np.cos(theta)

    def _rotate_z(self, theta):
        self._rotation_matrix_z[0, 0] = np.cos(theta)
        self._rotation_matrix_z[0, 1] = -np.sin(theta)
        self._rotation_matrix_z[1, 0] = np.sin(theta)
        self._rotation_matrix_z[1, 1] = np.cos(theta)

    @property
    def matrix(self):
        # Translate-Rotate-Scale
        return (self._scaling_matrix @
                self._rotation_matrix_z @ self._rotation_matrix_y @ self._rotation_matrix_x @
                self._translation_matrix).astype(float).T

    @matrix.setter
    def matrix(self, value):
        pass


class DroneViz(mglw.WindowConfig):
    """Base class with built in 3D camera support"""
    title = "DroneViz"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = 1.0
    window_size = 1024, 1024
    resizable = False
    samples = 4

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = True
        self.render_program = self.load_program('my_shader.glsl')
        # projection = pyrr.matrix44.create_perspective_projection(90, self.aspect_ratio, 1, 100, dtype='f4')

        self.render_program['projection'].write(self.camera.projection.tobytes())
        self.model_matrix = ModelMatrix()

        self.render_program['model'].write(self.model_matrix.matrix.astype('f4').tobytes())
        self.render_program['m_camera'].write(self.camera.matrix.astype('f4').tobytes())
        self.cube = geometry.cube(size=(1.0, 1.0, 1.0))

    def render(self, time, frame_time):
        self.ctx.clear(0)
        self.ctx.enable(moderngl.BLEND)
        self.render_program['model'].write(self.model_matrix.matrix.astype('f4').tobytes())

        # self.render_program['time'].value = min(time / 1, 1.0)
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
