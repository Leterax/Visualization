from pathlib import Path

import moderngl_window
import numpy as np
from moderngl_window import geometry


class Voronoi(moderngl_window.WindowConfig):
    title = "Water"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = 16 / 9
    window_size = 1280, 720
    resizable = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quad_fs = geometry.quad_fs()
        self.n = 100

        self.voronoi_program = self.load_program('my_shader.glsl')
        self.voronoi_program['iResolution'].value = (self.wnd.buffer_size[0], self.wnd.buffer_size[1])

        self.seeds = np.random.random_sample((self.n, 2))
        self.voronoi_program['seeds'].write(self.seeds.astype('f4').tobytes())
        colors = np.random.random_sample((self.n, 3))
        self.voronoi_program['seed_colors'].write(colors.astype('f4').tobytes())

        self.velocities = (np.random.random_sample((self.n, 2))-.5) / 250

        self.voronoi_program['seed_count'].value = self.n

    def render(self, time, frame_time):
        self.quad_fs.render(self.voronoi_program)
        self.seeds += self.velocities
        self.seeds = np.mod(self.seeds, 1)
        self.voronoi_program['seeds'].write(self.seeds.astype('f4').tobytes())


if __name__ == '__main__':
    moderngl_window.run_window_config(Voronoi)
