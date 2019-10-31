import time
from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np


class BasicWindowConfig(mglw.WindowConfig):
    """Minimal WindowConfig example"""
    gl_version = (3, 3)
    title = "Basic Window Config"
    resource_dir = Path(__file__).parent.parent.absolute() / 'resources'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.load_program("shader.glsl")
        self.prog['time'].value = 0.5

        n = 1_000_000
        vertices = (np.random.random_sample((n, 2)) - .5) * 2
        # target = render_text_perimeter_balls("Hey!", scale=300, pos=(75, 250))
        target = (np.random.random_sample((n, 2)) - .5) * 2

        self.vbo_1 = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vbo_2 = self.ctx.buffer(target.astype('f4').tobytes())

        self.vao = self.ctx.vertex_array(
            self.prog, [
                (self.vbo_1, '2f4', 'in_position'),
                (self.vbo_2, '2f4', 'target')
            ]
        )

    def render(self, time, frametime):
        self.ctx.clear(0)
        self.prog['time'].value = min(time / 10, 1.0)
        self.vao.render(mode=moderngl.POINTS)


if __name__ == '__main__':
    time.sleep(2)
    mglw.run_window_config(BasicWindowConfig)
