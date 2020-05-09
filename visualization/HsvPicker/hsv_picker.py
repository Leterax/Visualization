from pathlib import Path

import moderngl_window
from moderngl_window import geometry


class HSV(moderngl_window.WindowConfig):
    title = "HsvPicker Color Wheel"
    resource_dir = (Path(__file__) / "../resources").absolute()
    aspect_ratio = None
    window_size = 720, 720
    resizable = False
    samples = 8

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.quad_fs = geometry.quad_fs()

        self.hsv_program = self.load_program("hsv_picker_shader.glsl")
        self.hsv_program["wnd_size"].value = self.wnd.buffer_size

        # change this if you want it to go faster/slower
        self.hsv_program["speed"].value = 0.25

    def render(self, time: float, frame_time: float) -> None:
        self.hsv_program["time"].value = time
        self.quad_fs.render(self.hsv_program)


if __name__ == "__main__":
    HSV.run()
