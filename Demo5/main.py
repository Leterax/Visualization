from pathlib import Path

import moderngl
import moderngl_window
import numpy as np
from moderngl_window.geometry import quad_fs
from moderngl_window.opengl.vao import VAO


def f(n, x):
    out = (np.random.random((n, 2)) - .5) * (x / .5)
    out[out < 0] -= 1 - x
    out[out > 0] += 1 - x
    return out


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

        n = 3 ** 13  # 2**24 = 16_777_216
        self.render_boids['size'].value = 0.01
        self.render_boids['num_boids'].value = n

        positions = ((np.random.random_sample((n, 2)) - .5) * 2.) * 100
        velocities = f(n, .75) * 2.
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
        self.boids_vao_1.transform(self.boid_logic, self.boids_buffer_2)
        # update their positions
        self.boids_vao_2.transform(self.move_program, self.boids_buffer_1)

        # render boids to screen
        self.wnd.fbo.use()
        self.boids_vao_1.render(self.render_boids, mode=moderngl.POINTS)
        # if math.isnan(struct.unpack('6f', self.boids_buffer_1.read()[0:24])[0]):
        #    print("uh oh")
        # v = struct.unpack('6f', self.boids_buffer_1.read()[0:24])
        # print(f"boid1: ({v[-2]:.3f}, {v[-1]:.3f})")
        # print(f"boid2: {struct.unpack('6f', self.boids_buffer_1.read()[24:24*2])}")
        # print(f"boid3: {struct.unpack('6f', self.boids_buffer_1.read()[24*2:24*3])}")
        # print(f"boid4: {struct.unpack('6f', self.boids_buffer_1.read()[24*3:24*4])}")

        # self.boids_vao_1, self.boids_vao_2 = self.boids_vao_2, self.boids_vao_1
        # self.boids_buffer_1, self.boids_buffer_2 = self.boids_buffer_2, self.boids_buffer_1


if __name__ == '__main__':
    # noinspection PyTypeChecker
    moderngl_window.run_window_config(Boids)
