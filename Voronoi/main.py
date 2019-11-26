from pathlib import Path

import moderngl_window
import numpy as np
from moderngl_window import geometry


class Voronoi(moderngl_window.WindowConfig):
    title = "Voronoi"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = 1.0
    window_size = 1024, 1024
    resizable = False
    samples = 8

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quad_fs = geometry.quad_fs()
        self.n = 512

        self.voronoi_program = self.load_program('my_shader.glsl')
        self.voronoi_program['iResolution'].value = (self.wnd.buffer_size[0], self.wnd.buffer_size[1])

        self.seeds = np.random.random_sample((self.n, 2))
        self.seeds_buffer = self.ctx.buffer(data=self.seeds.astype('f4').tobytes())

        colors = np.random.random_sample((self.n, 3))
        self.color_buffer = self.ctx.buffer(data=colors.astype('f4').tobytes())

        self.velocities = (np.random.random_sample((self.n, 2))-.5) / 250

        self.voronoi_program['Seeds'].binding = 0
        self.voronoi_program['Colors'].binding = 1

    def render(self, time, frame_time):
        self.seeds_buffer.bind_to_uniform_block(0)
        self.color_buffer.bind_to_uniform_block(1)
        self.quad_fs.render(self.voronoi_program)
        self.seeds += self.velocities
        self.seeds = np.mod(self.seeds, 1)
        self.seeds_buffer.write(self.seeds.astype('f4').tobytes())


if __name__ == '__main__':
    # noinspection PyTypeChecker
    moderngl_window.run_window_config(Voronoi)
