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
    samples = 2

    # app settings
    # DIM = (7680, 4320)
    DIM = (12400, 7200)
    kernel_size = 3
    # fps to update the game at, not the screen
    fps = 60

    consts = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # load programs
        self.compute_shader = self.load_compute('compute_shader.glsl', self.consts)
        self.program = self.load_program('my_shader.glsl')
        self.world_generation_program = self.load_program('generate_world.glsl')

        self.quad_fs = quad_fs()
        self.program['texture0'] = 0

        self.zoom = 0.0025
        self.program['scale'] = self.zoom
        self.zoom_center = (0.5, 0.5)
        self.program['scaleCenter'].value = self.zoom_center

        # create the two textures
        load_image = False
        if load_image:
            self.texture01 = self.load_texture_2d('acorn.png')
            self.texture02 = self.load_texture_2d('acorn.png')
        else:
            self.texture01 = self.ctx.texture(self.DIM, 4, dtype='f1')
            self.texture02 = self.ctx.texture(self.DIM, 4, dtype='f1')
            self.generate_world()

        self.texture01.filter = moderngl.NEAREST, moderngl.NEAREST
        self.texture01.repeat_x, self.texture01.repeat_y = False, False
        self.texture02.filter = moderngl.NEAREST, moderngl.NEAREST
        self.texture02.repeat_x, self.texture02.repeat_y = False, False

        self.toggle = False

        self.last_frame = -10

    def render(self, time: float, frame_time: float) -> None:
        self.ctx.enable(moderngl.BLEND)
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)

        # slow down to our fps
        if time - self.last_frame > 1 / self.fps:
            self.last_frame = time

            # bind the textures
            self.texture01.bind_to_image(self.toggle, read=True, write=True)
            self.texture02.bind_to_image(not self.toggle, read=True, write=True)

            # run the compute shader
            w, h = self.texture01.size
            group_size_x = int(ceil(w / self.kernel_size))
            group_size_y = int(ceil(h / self.kernel_size))
            self.compute_shader.run(group_size_x, group_size_y, 1)

            self.toggle = not self.toggle

        # but we always want to display the world, at 60 fps
        # render the result
        [self.texture01, self.texture02][not self.toggle].use(location=0)
        self.quad_fs.render(self.program)

    def load_compute(self, uri: str, consts: dict) -> moderngl.ComputeShader:
        """Read compute shader code and set consts."""
        with open(self.resource_dir / uri, 'r') as fp:
            content = fp.read()

        # feed constant values
        for key, value in consts.items():
            content = content.replace(f"0//%{key}%", str(value))

        return self.ctx.compute_shader(content)

    def generate_world(self) -> None:
        """Generates a world randomly and render it to both textures."""
        fbo_1 = self.ctx.framebuffer(color_attachments=[self.texture02, self.texture01])
        fbo_1.use()
        self.quad_fs.render(self.world_generation_program)
        self.wnd.fbo.use()

    def mouse_drag_event(self, x: float, y: float, dx: float, dy: float) -> None:
        self.zoom_center = ((self.zoom_center[0] - dx / (1 / self.zoom) / self.window_size[0] * 3),
                            (self.zoom_center[1] + dy / (1 / self.zoom) / self.window_size[1] * 3))
        self.program['scaleCenter'].value = self.zoom_center

    def mouse_scroll_event(self, x_offset: float, y_offset: float) -> None:
        if y_offset > 0:
            self.zoom /= 1.5
        else:
            self.zoom *= 1.5

        self.zoom = max(0.0025, min(1, self.zoom))
        self.program['scale'] = self.zoom


if __name__ == '__main__':
    # noinspection PyTypeChecker
    mglw.run_window_config(GameOfLife)
