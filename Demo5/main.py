from pathlib import Path

import moderngl
import moderngl_window
import numpy as np
from moderngl_window.geometry import quad_fs
from moderngl_window.opengl.vao import VAO


class Boids(moderngl_window.WindowConfig):
    title = "Boids"
    resource_dir = (Path(__file__) / '../resources').absolute()
    aspect_ratio = None
    window_size = 1024, 1024
    resizable = False
    samples = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.move_program = self.load_program('move_boids.glsl')
        self.render_boids = self.load_program('render_boids.glsl')
        self.boid_logic = self.load_program('locality_info.glsl')
        self.boid_points = self.load_program('boid_points.glsl')
        self.debug_texture = self.load_program('texture.glsl')

        self.texture_1 = self.ctx.texture(self.wnd.buffer_size, 4, dtype='f4')
        # self.texture_2 = self.ctx.texture(self.wnd.buffer_size, 4, dtype='f4')
        self.fbo_1 = self.ctx.framebuffer(color_attachments=[self.texture_1])
        # self.fbo_2 = self.ctx.framebuffer(color_attachments=[self.texture_2])

        n = 2 ** 2  # 2**24 = 16_777_216
        self.render_boids['size'].value = 0.01
        self.render_boids['num_boids'].value = n

        positions = (np.random.random_sample((n, 2)) - .5) * 2.
        velocities = (np.clip(np.random.random_sample((n, 2)), a_min=0.25, a_max=None) - .5) / 100.
        acceleration = np.zeros((n, 2))
        pos_vel = np.array([*zip(positions.tolist(), velocities.tolist(), acceleration.tolist())]).flatten().astype(
            'f4')

        self.boids_buffer_1 = self.ctx.buffer(pos_vel)
        self.boids_buffer_2 = self.ctx.buffer(reserve=pos_vel.nbytes)

        self.boids_vao_1 = VAO(name='boids_1')
        self.boids_vao_1.buffer(self.boids_buffer_1, '2f 2f 2f', ['in_position', 'in_velocity', 'in_acceleration'])

        self.boids_vao_2 = VAO(name='boids_2')
        self.boids_vao_2.buffer(self.boids_buffer_2, '2f 2f 2f', ['in_position', 'in_velocity', 'in_acceleration'])

        self.boid_logic['texture0'].value = 0

        self.debug = quad_fs()
        self.debug_texture['texture0'].value = 0

    def render(self, time, frame_time):
        # self.program['time'].value = time
        self.ctx.clear(51 / 255, 51 / 255, 51 / 255)
        # render info to texture
        self.fbo_1.use()
        self.boids_vao_1.render(self.boid_points, mode=moderngl.POINTS)

        # output updated velocity
        # self.boids_vao_1.transform(self.boid_logic, self.boids_buffer_2)
        # update their positions
        self.boids_vao_1.transform(self.move_program, self.boids_buffer_2)

        # render boids to screen
        self.wnd.fbo.use()
        self.boids_vao_1.render(self.render_boids, mode=moderngl.POINTS)

        self.boids_vao_1, self.boids_vao_2 = self.boids_vao_2, self.boids_vao_1
        self.boids_buffer_1, self.boids_buffer_2 = self.boids_buffer_2, self.boids_buffer_1


if __name__ == '__main__':
    # noinspection PyTypeChecker
    moderngl_window.run_window_config(Boids)
