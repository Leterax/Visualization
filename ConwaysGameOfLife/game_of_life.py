from math import ceil
from pathlib import Path

import moderngl
from moderngl_window.geometry import quad_fs
import moderngl_window as mglw


class GameOfLife(mglw.WindowConfig):
    # moderngl_window settings
    gl_version = (4, 3)
    title = "GameOfLife"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1240, 720
    resizable = True
    samples = 4

    # app settings
    DIM = (7680, 4320)
    # DIM = (15_000, 15_000)
    kernel_size = 3

    consts = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # load programs
        self.compute_shader = self.load_compute('compute_shader.glsl', self.consts)
        self.program = self.load_program('my_shader.glsl')
        self.world_generation_program = self.load_program('generate_world.glsl')

        self.quad_fs = quad_fs()
        self.program['texture0'] = 0

        # create the two textures
        self.texture01 = self.ctx.texture(self.DIM, 4, dtype='f1')
        self.texture02 = self.ctx.texture(self.DIM, 4, dtype='f1')
        # self.texture01 = self.load_texture_2d('l2.png')
        # self.texture02 = self.load_texture_2d('l2.png')
        print(self.texture02.components, self.texture02.dtype)
        self.generate_world()
        self.texture01.filter = moderngl.NEAREST, moderngl.NEAREST
        self.texture02.filter = moderngl.NEAREST, moderngl.NEAREST

        self.toggle = False

    def render(self, time: float, frame_time: float) -> None:
        self.ctx.enable(moderngl.BLEND)
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)

        # bind the textures
        self.texture01.bind_to_image(self.toggle, read=True, write=True)
        self.texture02.bind_to_image(not self.toggle, read=True, write=True)

        # run the compute shader
        w, h = self.texture01.size
        group_size_x = int(ceil(w / self.kernel_size))
        group_size_y = int(ceil(h / self.kernel_size))
        self.compute_shader.run(group_size_x, group_size_y, 1)

        # render the result
        [self.texture01, self.texture02][self.toggle].use(location=0)
        self.quad_fs.render(self.program)

        self.toggle = not self.toggle

    def load_compute(self, uri: str, consts: dict) -> moderngl.ComputeShader:
        """Read compute shader code and set consts."""
        with open(self.resource_dir / uri, 'r') as fp:
            content = fp.read()

        # feed constant values
        for key, value in consts.items():
            content = content.replace(f"0//%{key}%", str(value))

        return self.ctx.compute_shader(content)

    def generate_world(self):
        fbo_1 = self.ctx.framebuffer(color_attachments=[self.texture02, self.texture01])
        fbo_1.use()
        self.quad_fs.render(self.world_generation_program)
        self.wnd.fbo.use()


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(GameOfLife)
