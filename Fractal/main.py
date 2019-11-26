import math
from pathlib import Path

import moderngl_window
from moderngl_window.geometry import quad_fs


class Fractal(moderngl_window.WindowConfig):
    title = "Fractal"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 720, 720
    resizable = True
    samples = 16

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quad_fs = quad_fs()

        self.fractal_program = self.load_program('my_shader.glsl')
        self.fractal_program['wnd_size'].value = self.wnd.buffer_size

        self.fractal_program['c'].value = (-0.7269, 0.1889)
        self.fractal_program['iter'].value = 1000
        self.fractal_program['R'].value = 2

        self.zoom = 1
        self.center = (0, 0)

    def render(self, time, frame_time):
        # self.fractal_program['time'].value = time

        # self.fractal_program['c'].value = (math.sin(time), math.cos(time))
        self.zoom = ((math.sin(time / 2) + 1) / 2) * 1024 + 1
        self.fractal_program['center'].value = self.center
        self.fractal_program['zoom'].value = 1 / self.zoom
        self.quad_fs.render(self.fractal_program)

    def mouse_drag_event(self, x, y, dx, dy):
        self.center = ((self.center[0] - dx / self.zoom / self.window_size[0]),
                       (self.center[1] + dy / self.zoom / self.window_size[1]))

    def mouse_scroll_event(self, x_offset, y_offset):
        if y_offset > 0:
            self.zoom += self.zoom
        else:
            self.zoom -= math.log2(self.zoom)


if __name__ == '__main__':
    moderngl_window.run_window_config(Fractal)
