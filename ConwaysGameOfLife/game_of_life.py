from math import ceil
from pathlib import Path

import numpy as np

import moderngl
from moderngl_window.geometry import quad_fs
import moderngl_window as mglw


class GameOfLife(mglw.WindowConfig):
    # moderngl_window settings
    gl_version = (4, 3)
    title = "GameOfLife"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1280, 720
    resizable = False
    samples = 4

    # app settings
    N = 128
    compute_size = min(3, N)
    num_group = int(ceil(N / 3))

    consts = {
        "COMPUTE_SIZE": compute_size
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # load programs
        self.compute_shader = self.load_compute('compute_shader.glsl', self.consts)
        self.program = self.load_program('my_shader.glsl')

        self.compute_shader['input_image'] = 0
        self.compute_shader['output_image'] = 1

        # create the two textures
        self.texture01 = self.ctx.texture((256, 256), 1, dtype='f4')
        self.texture02 = self.ctx.texture((256, 256), 1, dtype='f4')
        self.texture01.filter = moderngl.NEAREST, moderngl.NEAREST
        self.texture02.filter = moderngl.NEAREST, moderngl.NEAREST

        data = np.ones((256, 256), dtype='f4')
        self.texture02.write(data)

        # bind the textures
        self.texture01.bind_to_image(0, read=True, write=True)
        self.texture02.bind_to_image(1, read=True, write=True)

        self.quad_fs = quad_fs()
        self.program['texture0'] = 1

    def render(self, time: float, frame_time: float) -> None:
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)

        # bind the textures
        self.texture01.bind_to_image(0, read=True, write=False)
        self.texture02.bind_to_image(1, read=False, write=True)

        # run the compute shader
        w, h = self.texture01.size
        group_size_x = int(w/3)
        group_size_y = int(h/3)
        self.compute_shader.run(group_x=group_size_x, group_y=group_size_y)

        # render the result
        self.texture02.use(location=1)
        self.quad_fs.render(self.program)

    def load_compute(self, uri: str, consts: dict) -> moderngl.ComputeShader:
        """Read compute shader code and set consts."""
        with open(self.resource_dir / uri, 'r') as fp:
            content = fp.read()

        # feed constant values
        for key, value in consts.items():
            content = content.replace(f"0//%{key}%", str(value))

        return self.ctx.compute_shader(content)


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(GameOfLife)
