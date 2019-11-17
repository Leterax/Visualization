import struct
from pathlib import Path

import moderngl
import moderngl_window
import numpy as np


class Boids(moderngl_window.WindowConfig):
    title = "Boids"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 720, 720
    resizable = False
    samples = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.program = self.load_program('my_shader.glsl')
        self.render_boids = self.load_program('render_boids.glsl')

        n = 512

        positions = np.random.random_sample((n, 3))
        velocities = np.random.random_sample((n, 3)) / 2.
        pos_vel = np.array([*zip(positions.tolist(), velocities.tolist())]).flatten().astype('f4')

        self.vbo_1 = self.ctx.buffer(pos_vel.tobytes())
        self.vbo_2 = self.ctx.buffer(reserve=pos_vel.nbytes)

        self.vao_1 = self.ctx.vertex_array(
            self.program, [
                (self.vbo_1, '2f4 2f4', 'in_position', 'in_velocity'),
            ]
        )

        self.vao_2 = self.ctx.vertex_array(
            self.program, [
                (self.vbo_2, '2f4 2f4', 'in_position', 'in_velocity'),
            ]
        )

        self.vao_3 = self.ctx.vertex_array(
            self.render_boids, [
                (self.vbo_1, '2f4 2x4', 'in_position'),
            ]
        )

        self.vao_4 = self.ctx.vertex_array(
            self.render_boids, [
                (self.vbo_2, '2f4 2x4', 'in_position'),
            ]
        )

        # self.program['wnd_size'].value = self.wnd.buffer_size

    def render(self, time, frame_time):
        # self.program['time'].value = time
        self.vao_3.render(mode=moderngl.POINTS)
        self.vao_1.transform(self.vbo_2)

        self.vao_1, self.vao_2 = self.vao_2, self.vao_1
        self.vbo_1, self.vbo_2 = self.vbo_2, self.vbo_1
        self.vao_3, self.vao_4 = self.vao_4, self.vao_3
        # print(struct.unpack('4f', self.vbo_2.read()[:16]))
        # self.vao_2.render(mode=moderngl.POINTS)


if __name__ == '__main__':
    moderngl_window.run_window_config(Boids)
