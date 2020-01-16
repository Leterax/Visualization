"""
    Example of using a compute shader.
    Bounce particles of walls.

    requirements:
     - moderngl_window
     - pyrr
     - matplotlib

    author: Leterax
"""
from math import ceil
from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
from matplotlib.colors import hsv_to_rgb
from moderngl_window.geometry import bbox, sphere
from pyrr.matrix44 import create_from_eulers as rotate
from pyrr.matrix44 import create_from_translation as translation
from pyrr.matrix44 import create_perspective_projection as perspective
from pyrr.matrix44 import multiply


class ComputeShaderExample(mglw.WindowConfig):
    gl_version = (4, 3)
    title = "ComputeShader Example"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = False
    samples = 2

    N = 256
    # if `N` is below 64 use it as the number of workers. If `N` is larger use larger worker groups
    consts = {
        "COMPUTE_SIZE": min(64, N),
        "BALL_SIZE": .01,
        "BOX_SIZE": .5,
    }
    NUM_GROUP = int(ceil(N / 64))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # load programs
        self.compute_shader = self.load_compute('compute_shader.glsl', self.consts)
        self.render_program = self.load_program('points.glsl')
        self.render_program = self.load_program('balls.glsl')
        self.box_program = self.load_program('box.glsl')

        # set projection matrices
        projection_matrix = perspective(60, self.wnd.aspect_ratio, .1, 100).astype('f4')
        camera_matrix = translation((0, 0, -2)).astype('f4')
        self.render_program['m_projection'].write(projection_matrix.tobytes())
        self.render_program['m_camera'].write(camera_matrix.tobytes())

        # generate random positions and velocities
        pos_vel = self.generate_data()
        # generate N hsv colors
        _rgb_colors = np.array((np.arange(self.N) / self.N, np.full(self.N, .7), np.full(self.N, .5))).T
        # convert to grb
        colors = hsv_to_rgb(_rgb_colors)
        # reshape into vec4; [h, s, v] -> [h, s, v, 0.]
        colors = np.c_[colors, np.ones(colors.shape[0])]

        # create two buffers to switch between
        self.buffer1 = self.ctx.buffer(pos_vel)
        self.buffer2 = self.ctx.buffer(reserve=pos_vel.nbytes)

        self.colors = self.ctx.buffer(colors.astype('f4'))

        # create a VAO with buffer 1 bound to it to render the balls
        self.ball = sphere(radius=.01, rings=4, sectors=4)
        self.ball.buffer(self.buffer1, '3f 3f/i', ['ball_position', 'ball_velocity'])
        self.ball.buffer(self.colors, '4f/i', ['ball_color'])

        # bind the buffers to 1 and 0 respectively
        self._toggle = False
        self.buffer1.bind_to_storage_buffer(self._toggle)
        self.buffer2.bind_to_storage_buffer(not self._toggle)

        # box vao
        self.box = bbox()
        self.box_program['m_projection'].write(projection_matrix.tobytes())
        self.box_program['m_camera'].write(camera_matrix.tobytes())

    def render(self, time, frame_time):
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)
        self.ctx.enable(moderngl.BLEND)

        # rotate and translate the camera for a smooth rotating movement
        t = translation((0, 0, -2), dtype='f4')
        rotation = rotate((0, 0, time / 3.), dtype='f4')
        cam_matrix = multiply(rotation, t)

        # render the box
        self.render_program['m_camera'].write(cam_matrix)
        self.box_program['m_camera'].write(cam_matrix)
        self.box.render(self.box_program)

        # run the compute shader
        self.compute_shader.run(group_x=self.NUM_GROUP)
        # render the result to the screen
        self.ball.render(self.render_program, instances=self.N)

        # swap buffers
        self._toggle = not self._toggle
        self.buffer1.bind_to_storage_buffer(self._toggle)
        self.buffer2.bind_to_storage_buffer(not self._toggle)

    def load_compute(self, uri, consts):
        """ read compute shader code and set consts """
        with open(self.resource_dir / uri, 'r') as fp:
            content = fp.read()

        # feed constant values
        for key, value in consts.items():
            content = content.replace(f"0//%{key}%", str(value))

        return self.ctx.compute_shader(content)

    def generate_data(self):
        positions = (np.random.random((self.N, 3)) - .5) / 2.
        velocities = (np.random.random((self.N, 3)) - .5) * (.75 / .5)
        velocities[velocities < 0] -= 1 - .75
        velocities[velocities > 0] += 1 - .75
        velocities /= 100.
        return np.column_stack((positions, velocities)).flatten().astype('f4')


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(ComputeShaderExample)
