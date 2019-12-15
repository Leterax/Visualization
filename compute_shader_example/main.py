from math import ceil
from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
from matplotlib.colors import hsv_to_rgb
from moderngl_window.opengl.vao import VAO
from moderngl_window.scene.camera import KeyboardCamera


class ComputeShaderExample(mglw.WindowConfig):
    gl_version = (4, 3)
    title = "ComputeShader Example"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = False
    samples = 16

    N = 2 ** 6
    # if `N` is below 1024 use it as the number of workers. If `N` is larger use larger worker groups
    consts = {
        "COMPUTE_SIZE": min(1024, N),
    }
    NUM_GROUP = int(ceil(N / 1024))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera.set_position(0, 0, 1)

        self.ctx.point_size = 3

        # load programs
        self.compute_shader = self.load_compute('compute_shader.glsl', self.consts)
        self.render_program = self.load_program('points.glsl')

        # set projection matrices
        self.render_program['m_projection'].write(self.camera.projection.tobytes())
        self.render_program['m_camera'].write(self.camera.matrix.astype('f4').tobytes())

        # generate random positions and velocities
        positions = np.random.random((self.N, 3)).astype('f4')
        velocities = np.random.random((self.N, 3)).astype('f4')
        # shift_to_center
        positions = (positions - .5) * 2.
        velocities = (velocities - .5) * 2.
        # pad to make it a vec4
        positions = np.c_[positions, np.ones(positions.shape[0])]
        velocities = np.c_[velocities, np.zeros(velocities.shape[0])]

        velocities = velocities / 100.

        # generate N hsv colors
        _rgb_colors = np.array((np.arange(self.N) / self.N, np.full(self.N, .7), np.full(self.N, .5))).T
        # convert to grb
        colors = hsv_to_rgb(_rgb_colors)
        # reshape into vec4; [h, s, v] -> [h, s, v, 0.]
        colors = np.c_[colors, np.ones(colors.shape[0])]

        # interleave data
        pos_vel_color = np.array([*zip(positions.tolist(), velocities.tolist(), colors.tolist())]).flatten().astype(
            'f4')

        # create two buffers to switch between
        self.buffer1 = self.ctx.buffer(pos_vel_color)
        self.buffer2 = self.ctx.buffer(reserve=pos_vel_color.nbytes)

        # create a VAO with buffer 1 bound to it to render the balls
        self.render_vao = VAO(name='render_vao')
        self.render_vao.buffer(self.buffer1, '4f 4f 4f', ['in_position', 'in_velocity', 'in_color'])

        # bind the buffers to 1 and 0 respectively
        self._toggle = False
        self.buffer1.bind_to_storage_buffer(self._toggle)
        self.buffer2.bind_to_storage_buffer(not self._toggle)

    def render(self, time, frame_time):
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        # run the compute shader
        self.compute_shader.run(group_x=self.NUM_GROUP)
        # render the result to the screen
        self.render_vao.render(self.render_program, mode=moderngl.POINTS)

        # swap buffers
        self._toggle = not self._toggle
        self.buffer1.bind_to_storage_buffer(self._toggle)
        self.buffer2.bind_to_storage_buffer(not self._toggle)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)

    def load_compute(self, uri, consts):
        """ read gl code """
        with open(self.resource_dir / uri, 'r') as fp:
            content = fp.read()

        # feed constant values
        for key, value in consts.items():
            content = content.replace(f"0//%{key}%", str(value))

        return self.ctx.compute_shader(content)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(ComputeShaderExample)
