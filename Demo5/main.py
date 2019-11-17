from pathlib import Path

import moderngl_window
from moderngl_window import geometry


class Gradient(moderngl_window.WindowConfig):
    title = "Voronoi"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 720, 720
    resizable = False
    samples = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quad_fs = geometry.quad_fs()

        self.gradient_program = self.load_program('my_shader.glsl')
        self.gradient_program['wnd_size'].value = self.wnd.buffer_size
        self.gradient_program['speed'].value = 7.5

    def render(self, time, frame_time):
        self.gradient_program['time'].value = time
        self.quad_fs.render(self.gradient_program)


if __name__ == '__main__':
    moderngl_window.run_window_config(Gradient)
