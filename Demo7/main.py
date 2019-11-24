from pathlib import Path

import moderngl_window
from moderngl_window.geometry import quad_fs


class Fractal(moderngl_window.WindowConfig):
    title = "Gradient"
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

        self.fractal_program['c'].value = (.5, .5)
        self.fractal_program['iter'].value = 10000

        self.zoom = 1
        self.center = (0, 0)

    def render(self, time, frame_time):
        top_left = (self.center[0] + -1 / self.zoom, self.center[1] + 1 / self.zoom)
        bottom_right = (self.center[0] + 1 / self.zoom, self.center[1] + -1 / self.zoom)
        self.fractal_program['box'].value = (*top_left, *bottom_right)

        self.quad_fs.render(self.fractal_program)

    def mouse_drag_event(self, x, y, dx, dy):
        self.center = ((self.center[0] + -dx / self.window_size[0]), (self.center[1] - dy / self.window_size[1]))

    def mouse_scroll_event(self, x_offset, y_offset):
        self.zoom += y_offset
        print(self.zoom)


if __name__ == '__main__':
    moderngl_window.run_window_config(Fractal)
