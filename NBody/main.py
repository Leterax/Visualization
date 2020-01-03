"""
    Example of using a compute shader.
    Bounce particles of walls.

    requirements:
     - moderngl_window
     - pyrr

    author: Leterax
"""
import struct
from math import ceil
from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
from matplotlib.colors import hsv_to_rgb
# from moderngl_window.geometry import bbox
from moderngl_window.opengl.vao import VAO
from pyrr.matrix44 import create_from_translation as translation
from pyrr.matrix44 import create_perspective_projection as perspective

sun = {"location": (0, 0, 0), "mass": 2e30, "velocity": (0, 0, 0)}
mercury = {"location": (0, 5.7e10, 0), "mass": 3.285e23, "velocity": (47000, 0, 0)}
venus = {"location": (0, 1.1e11, 0), "mass": 4.8e24, "velocity": (35000, 0, 0)}
earth = {"location": (0, 1.5e11, 0), "mass": 6e24, "velocity": (30000, 0, 0)}
mars = {"location": (0, 2.2e11, 0), "mass": 2.4e24, "velocity": (24000, 0, 0)}
jupiter = {"location": (0, 7.7e11, 0), "mass": 1e28, "velocity": (13000, 0, 0)}
saturn = {"location": (0, 1.4e12, 0), "mass": 5.7e26, "velocity": (9000, 0, 0)}
uranus = {"location": (0, 2.8e12, 0), "mass": 8.7e25, "velocity": (6835, 0, 0)}
neptune = {"location": (0, 4.5e12, 0), "mass": 1e26, "velocity": (5477, 0, 0)}
pluto = {"location": (0, 3.7e12, 0), "mass": 1.3e22, "velocity": (4748, 0, 0)}

planets = [sun]  # , mercury, venus, earth, mars, jupiter, saturn, uranus, neptune


class NBodySim(mglw.WindowConfig):
    gl_version = (4, 3)
    title = "N-Body Simulation"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = False
    samples = 16

    N = len(planets)
    # if `N` is below 1024 use it as the number of workers. If `N` is larger use larger worker groups
    consts = {
        "COMPUTE_SIZE": min(1024, N),
        "N": N,
        "E": 0.1 ** 2.,
        "DT": 24 * 60 * 60
    }
    NUM_GROUP = int(ceil(N / 1024))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx.point_size = 5

        # load programs
        self.calculate_force = self.load_compute('calculate_force.glsl', self.consts)
        self.move_planets = self.load_compute('move_planets.glsl', self.consts)
        self.render_program = self.load_program('points.glsl')
        # self.box_program = self.load_program('box.glsl')

        # set projection matrices
        projection_matrix = perspective(60, self.wnd.aspect_ratio, .1, 7e15).astype('f4')
        camera_matrix = translation((0, 0, -1e13)).astype('f4')
        self.render_program['m_projection'].write(projection_matrix.tobytes())
        self.render_program['m_camera'].write(camera_matrix.tobytes())

        # generate random positions and velocities
        positions = np.random.random((self.N, 3)).astype('f4')
        velocities = np.random.random((self.N, 3)).astype('f4')
        force = np.zeros((self.N, 3)).astype('f4')
        # shift_to_center
        positions = (positions - .5) * 2.
        velocities = (velocities - .5) * 2.
        # pad to make it a vec4
        positions = np.c_[positions, np.ones(positions.shape[0])]
        velocities = np.c_[velocities, np.ones(velocities.shape[0]) * 100.]
        force = np.c_[force, np.ones(force.shape[0])]

        for index, planet in enumerate(planets):
            velocities[index] = (*planet['velocity'], planet['mass'])
            positions[index] = (*planet['location'], 1)

        # print(positions)

        # generate N hsv colors
        _rgb_colors = np.array((np.arange(self.N) / self.N, np.full(self.N, .7), np.full(self.N, .5))).T
        # convert to grb
        colors = hsv_to_rgb(_rgb_colors).astype('f4')
        # reshape into vec4; [h, s, v] -> [h, s, v, 0.]
        colors = np.c_[colors, np.ones(colors.shape[0])]

        # interleave data
        interleaved = np.c_[positions, velocities, force, colors].flatten().astype('f4').tolist()
        interleaved = struct.pack('4d4f4f4f' * (len(interleaved) // 16), *interleaved)

        # create two buffers to switch between
        self.buffer1 = self.ctx.buffer(interleaved)
        self.buffer2 = self.ctx.buffer(reserve=len(interleaved))

        # create a VAO with buffer 1 bound to it to render the balls
        self.render_vao = VAO(name='render_vao')
        self.render_vao.buffer(self.buffer2, '4f8 4f 4f 4f', ['in_position', 'in_velocity', 'in_force', 'in_color'])

        # bind the buffers to 1 and 0 respectively
        self._toggle = False
        self.buffer1.bind_to_storage_buffer(self._toggle)
        self.buffer2.bind_to_storage_buffer(not self._toggle)

    def render(self, time, frame_time):
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)
        self.ctx.enable(moderngl.BLEND)

        # render the result to the screen
        # position
        print(struct.unpack('4d', self.buffer1.read()[:4 * 8]))
        # # velocity and mass
        # print(struct.unpack('4f', self.buffer1.read()[4 * 4:4 * 4 * 2]))
        # # force
        # print(struct.unpack('4f', self.buffer1.read()[4 * 4 * 2:4 * 4 * 3]))
        self.render_vao.render(self.render_program, mode=moderngl.POINTS)

        # run the compute shader
        self.calculate_force.run(group_x=self.NUM_GROUP)

        # swap buffers
        self._toggle = not self._toggle
        self.buffer1.bind_to_storage_buffer(self._toggle)
        self.buffer2.bind_to_storage_buffer(not self._toggle)

        self.move_planets.run(group_x=self.NUM_GROUP)

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


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(NBodySim)
