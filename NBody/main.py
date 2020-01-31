"""
    N-Body Simulation

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
from moderngl_window import screenshot
from moderngl_window.opengl.vao import VAO
from pyrr.matrix44 import create_from_translation as translation
from pyrr.matrix44 import create_perspective_projection as perspective

# planets use the format of "location" in AE, "mass" in Sun-mass, "velocity" in AE/s
sun = {"location": (0, 0, 0), "mass": 1.989e30 / 1.989e30, "velocity": (0, 0, 0), "force": (0, 0, 0)}
mercury = {"location": (0, 5.7e10 / 1.5e11, 0), "mass": 3.285e23 / 1.989e30, "velocity": (47e3 / 1.5e11, 0, 0),
           "force": (0, 0, 0)}
venus = {"location": (0, 1.1e11 / 1.5e11, 0), "mass": 4.8e24 / 1.989e30, "velocity": (35e3 / 1.5e11, 0, 0),
         "force": (0, 0, 0)}
earth = {"location": (0, 1.5e11 / 1.5e11, 0), "mass": 6e24 / 1.989e30, "velocity": (30e3 / 1.5e11, 0, 0),
         "force": (0, 0, 0)}
mars = {"location": (0, 2.2e11 / 1.5e11, 0), "mass": 2.4e24 / 1.989e30, "velocity": (24e3 / 1.5e11, 0, 0),
        "force": (0, 0, 0)}
jupiter = {"location": (0, 7.7e11 / 1.5e11, 0), "mass": 1e28 / 1.989e30, "velocity": (13e3 / 1.5e11, 0, 0),
           "force": (0, 0, 0)}
saturn = {"location": (0, 1.4e12 / 1.5e11, 0), "mass": 5.7e26 / 1.989e30, "velocity": (9e3 / 1.5e11, 0, 0),
          "force": (0, 0, 0)}
uranus = {"location": (0, 2.8e12 / 1.5e11, 0), "mass": 8.7e25 / 1.989e30, "velocity": (6.835e3 / 1.5e11, 0, 0),
          "force": (0, 0, 0)}
neptune = {"location": (0, 4.5e12 / 1.5e11, 0), "mass": 1e26 / 1.989e30, "velocity": (5.477e3 / 1.5e11, 0, 0),
           "force": (0, 0, 0)}

planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]


class NBodySim(mglw.WindowConfig):
    gl_version = (4, 3)
    title = "N-Body Simulation"
    resource_dir = (Path(__file__) / '../resources').absolute()
    take_screenshots = False
    screenshots_dir = (Path(__file__) / '../screen_recordings/uniform100').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = False
    samples = 16

    N = len(planets)
    # if `N` is below 64 use it as the number of workers. If `N` is larger use larger worker groups
    consts = {
        "COMPUTE_SIZE": min(64, N),
        "N": N,
        "DT": 60*30  # DT of 30 min
    }

    NUM_GROUP = int(ceil(N / 64))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx.point_size = 5

        # load programs
        self.calculate_force = self.load_compute('calculate_force.glsl', self.consts)
        self.move_planets = self.load_compute('move_planets.glsl', self.consts)
        self.render_program = self.load_program('points.glsl')

        # set projection matrices
        projection_matrix = perspective(60, self.wnd.aspect_ratio, .001, 7e15).astype('f4')
        # you might want to change the z component in order to zoom out further.
        camera_matrix = translation((0, 0, -4)).astype('f4')
        self.render_program['m_projection'].write(projection_matrix.tobytes())
        self.render_program['m_camera'].write(camera_matrix.tobytes())

        # set properties for making the gif
        mglw.settings.SCREENSHOT_PATH = self.screenshots_dir
        self.simulated_time = 0
        # take a picture every every 15 days of simulated time
        self.gif_interval = 60 * 60 * 24 * 15
        self._last_capture = float('-inf')

        # use predefined values
        positions = np.empty((self.N, 3)).astype('f4')
        velocities = np.empty((self.N, 3)).astype('f4')
        force = np.empty((self.N, 3)).astype('f4')
        mass = np.empty((self.N, 1)).astype('f4')

        for index, planet in enumerate(planets):
            velocities[index] = planet['velocity']
            positions[index] = planet['location']
            force[index] = planet['force']
            mass[index] = planet['mass']

        colors = np.array(
            [[255, 255, 0, 255], [171, 159, 111, 255], [128, 111, 43, 255],
             [8, 138, 41, 255], [255, 111, 0, 255], [171, 153, 138, 255],
             [145, 118, 94, 255], [214, 199, 186, 255], [67, 111, 181, 255]]) / 255

        # interleave data
        interleaved = list(zip(positions.tolist(), velocities.tolist(), force.tolist(), mass.tolist()))
        interleaved = [item for l in interleaved for sublist in l for item in sublist]
        interleaved = struct.pack('<' + '10d' * self.N, *interleaved)

        # create two buffers to switch between
        self.buffer1 = self.ctx.buffer(interleaved)
        self.buffer2 = self.ctx.buffer(reserve=len(interleaved))
        self.color_buffer = self.ctx.buffer(colors.astype('f4'))

        # create a VAO with buffer 1 bound to it to render the balls
        self.render_vao = VAO(name='render_vao')

        self.render_vao.buffer(self.buffer1, '3f8 3f8 3f8 1f8',
                               ['in_position', 'in_velocity', 'in_force', 'in_mass'])

        self.render_vao.buffer(self.color_buffer, '4f', ['in_color'])

        # bind the buffers to 1 and 0 respectively
        self._toggle = False
        self.buffer1.bind_to_storage_buffer(self._toggle)
        self.buffer2.bind_to_storage_buffer(not self._toggle)

    def render(self, time, frame_time):

        # render the result to the screen
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)
        self.ctx.enable(moderngl.BLEND)
        self.render_vao.render(self.render_program, mode=moderngl.POINTS)

        if self.take_screenshots and self.simulated_time - self._last_capture > self.gif_interval:
            # take a screenshot
            screenshot.create(self.wnd.fbo)
            self._last_capture = self.simulated_time

        # run the compute shader
        self.calculate_force.run(group_x=self.NUM_GROUP)
        # swap buffers
        self._swap_buffers()
        # run the compute shader
        self.move_planets.run(group_x=self.NUM_GROUP)
        # swap buffers
        self._swap_buffers()

        self.simulated_time += self.consts['DT']

    def _swap_buffers(self) -> None:
        """
        Swap the two buffers for the compute-shaders by re-binding them.

        :return: None
        """
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
