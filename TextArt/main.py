from pathlib import Path

import moderngl
import moderngl_window as mglw
import numpy as np
# noinspection PyUnresolvedReferences
from generate_text import render_text_perimeter_balls
from pyrr import matrix44


class TextArt(mglw.WindowConfig):
    """
    Render text assembling from balls.
    Press space to pause
    Drag mouse to scroll through time
    Use `add_text` to add more text to the scene.
    """
    gl_version = (3, 3)
    title = "TextArt"
    samples = 16
    resource_dir = Path(__file__).parent.joinpath('resources').resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.projection = matrix44.create_orthogonal_projection(0, self.wnd.size[0], 0, self.wnd.size[1], -1.0, 1.0,
                                                                dtype='f4')
        self.texts = []
        self.is_paused = False

        self.add_text("Text", 300, (300, 350), 5, (1, 0, 0))
        self.add_text("Art", 300, (150, 75), 5, (0, 1, 0))

    def add_text(self, text: str, scale: int, pos: tuple, ball_size: int, color: tuple):
        target = render_text_perimeter_balls(text, scale=scale, pos=pos[::-1], ball_size=ball_size)
        n = target.shape[0]
        vertices = np.random.random_sample((n, 2))
        vertices = np.array([vertices[:, 0] * self.window_size[0], vertices[:, 1] * self.window_size[1]]).T

        prog = self.load_program("shader.glsl")
        prog['time'].value = 0
        prog['m_proj'].write(self.projection.tobytes())

        prog['size'].value = ball_size
        prog['color'].value = color

        vbo_1 = self.ctx.buffer(vertices.astype('f4').tobytes())
        vbo_2 = self.ctx.buffer(target.astype('f4').tobytes())

        vao = self.ctx.vertex_array(
            prog, [
                (vbo_1, '2f4', 'in_position'),
                (vbo_2, '2f4', 'target')
            ]
        )

        self.texts.append((vao, prog))

    def render(self, time, frame_time):
        r = g = b = 51 / 255
        self.ctx.clear(r, g, b)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        for vao, prg in self.texts:
            prg['time'].value = min(time / 2., 1.)
            vao.render(mode=moderngl.POINTS)

    def mouse_drag_event(self, x, y, dx, dy):
        self.timer.time = max(0, min(x / self.wnd.buffer_width, 1))

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if action == keys.ACTION_PRESS:
            if key == keys.SPACE:
                self.timer.toggle_pause()


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(TextArt)
