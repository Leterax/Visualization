from pathlib import Path

import moderngl_window
from moderngl_window import geometry


class HSV(moderngl_window.WindowConfig):
    title = "HSV Color Wheel"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 720, 720
    resizable = False
    samples = 16

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quad_fs = geometry.quad_fs()

        self.hsv_program = self.load_program('my_shader.glsl')
        self.hsv_program['wnd_size'].value = self.wnd.buffer_size

        # change this if you want it to go faster/slower
        self.hsv_program['speed'].value = .25

    def render(self, time, frame_time):
        self.hsv_program['time'].value = time
        self.quad_fs.render(self.hsv_program)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    moderngl_window.run_window_config(HSV)
