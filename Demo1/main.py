import time
from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
# noinspection PyUnresolvedReferences
from generate_text import render_text_perimeter_balls
from pyrr import matrix44


class BasicWindowConfig(mglw.WindowConfig):
    """Minimal WindowConfig example"""
    gl_version = (3, 3)
    title = "Basic Window Config"
    resource_dir = Path(__file__).parent.joinpath('../resources').resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prog = self.load_program("shader.glsl")

        projection = matrix44.create_orthogonal_projection(0, self.wnd.size[0], 0, self.wnd.size[1], -1.0, 1.0,
                                                           dtype='f4')

        size = 1
        self.is_paused = False

        target = render_text_perimeter_balls("Hey!", scale=300, pos=(75, 250), ball_size=size)
        n = target.shape[0]
        vertices = np.random.random_sample((n, 2))
        vertices = np.array([vertices[:, 0] * self.window_size[0], vertices[:, 1] * self.window_size[1]]).T

        self.prog['time'].value = 0
        self.prog['m_proj'].write(projection.tobytes())

        self.prog['size'].value = size
        self.prog['color'].value = (1.0, 0.0, 0.0)

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
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        if not self.is_paused:
            self.prog['time'].value = min(time / 1, 1.0)
        self.vao.render(mode=moderngl.POINTS)

    def mouse_drag_event(self, x, y):
        self.prog['time'].value = max(0, min(x / self.wnd.buffer_width, 1))

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if action == keys.ACTION_PRESS:
            if key == keys.SPACE:
                self.is_paused = not self.is_paused
                self.timer.toggle_pause()


if __name__ == '__main__':
    time.sleep(2)
    mglw.run_window_config(BasicWindowConfig)
