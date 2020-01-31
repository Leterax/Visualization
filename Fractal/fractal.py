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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.quad_fs = quad_fs()

        self.fractal_program = self.load_program('my_shader.glsl')
        self.fractal_program['wnd_size'].value = self.wnd.buffer_size

        self.fractal_program['c'].value = (-0.7269, 0.1889)
        self.fractal_program['iter'].value = 1000
        self.fractal_program['R'].value = 2

        self.zoom = 1
        self.center = (0, 0)

    def render(self, time: float, frame_time: float) -> None:
        self.fractal_program['center'].value = self.center
        self.fractal_program['zoom'].value = 1 / self.zoom
        self.quad_fs.render(self.fractal_program)

    def mouse_drag_event(self, x: float, y: float, dx: float, dy: float) -> None:
        self.center = ((self.center[0] - dx / self.zoom / self.window_size[0]),
                       (self.center[1] + dy / self.zoom / self.window_size[1]))

    def mouse_scroll_event(self, x_offset: float, y_offset: float) -> None:
        if y_offset > 0:
            self.zoom += self.zoom
        else:
            self.zoom -= math.log2(self.zoom)

        print(self.zoom)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    moderngl_window.run_window_config(Fractal)
