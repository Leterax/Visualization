from timeit import default_timer as timer

import numba as nb
import numpy as np
from kivy.core.window import Window
from scipy.spatial import cKDTree
from skimage.draw import line, polygon

#from Display.Window import MyApp


def time_it(func):
    """
    A decorator to time functions. The function will no longer return a value.
    TODO: return the value
    :param func: function to be timed
    :return: the wrapped function
    """

    def wrapper(*args, **kwargs):
        start = timer()
        func(*args, **kwargs)
        print(timer() - start)

    return wrapper


def random_velocity():
    """
    Generate a random velocity based on some boundaries
    :return: a random velocity.
    """
    vel_dir = np.random.random(2) * 2 - 1
    vel = vel_dir * np.random.randint(2, 6)
    vel = np.where(np.abs(vel) > 1, vel, (vel / vel) * 1).astype(np.float16)
    return vel


def normalize(v):
    """
    Normalize a vector
    :param v: input vector
    :return: normalized output vector
    """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def rotate(xy, theta):
    """
    Rotate a point by an angle around the origin.
    :param xy: 2D point to be rotated
    :param theta: angle to be rotated by in radians
    :return: the rotated point
    """
    r = np.array(
        [xy[0] * np.cos(theta) - xy[1] * np.sin(theta),
         xy[0] * np.sin(theta) + xy[1] * np.cos(theta)]
    ).T
    return r


@nb.njit(parallel=True, fastmath=True, cache=True)
def numba_flat_apply_gradient(color_1, color_2, out, center):
    """
    A function to perform radial interpolation between two colors around a center-point at high speed
    :param color_1: the color to interpolate from
    :param color_2: the color to interpolate to
    :param out: the interpolated image
    :param center: point of radial interpolation
    :return: None
    """
    max_dst = (center[0]) ** 2 + (center[1]) ** 2
    width = out.shape[1]
    for xy in nb.prange(out.shape[0] * out.shape[1]):
        y = xy % width
        x = xy // width
        dst = (center[0] - x) ** 2 + (center[1] - y) ** 2
        c = (color_2 - color_1) * (dst / max_dst) + color_1
        out[x, y] = c


class BoidSimulation(MyApp):
    def __init__(self, n=75, res=(1000, 1000)):
        self.res = res
        self._clear = np.zeros((*self.res, 3), dtype=np.uint8)
        numba_flat_apply_gradient(color_1=np.array((115, 15, 30)) / 2, color_2=np.array((100, 10, 100)) / 2,
                                  out=self._clear,
                                  center=np.array((self.res[0] / 2, self.res[1] / 2)))
        self.data = np.copy(self._clear)

        self.boids = []

        walls = np.array(self.res)
        for _ in range(n):
            vel = random_velocity()
            position = np.random.randint(0, 1000, size=2).astype(np.float16)
            acceleration = np.zeros(2, dtype=np.float16)

            self.boids.append(Boid(position, vel, acceleration, walls, 6, view_radius=75))

        # a quadTree for spacial separation and faster lookup. O(n*log*n) instead of O(n**2)
        self.quadTree = cKDTree([boid.position for boid in self.boids])

        super().__init__(update=self.update, res=self.res)

    def update(self, set_data, *dt):
        # dt is the delta-time between frames.
        # clear the screen
        self.data[:] = self._clear

        # update the KDTree
        self.quadTree = cKDTree([boid.position for boid in self.boids], leafsize=8)

        # loop over boids
        for boid in self.boids:
            # query_ball_point returns the indices, not the objects so we quickly look them up.
            other_boids = [self.boids[i] for i in
                           self.quadTree.query_ball_point(boid.position, boid.view_radius)]

            # adding some weights makes it look slightly more natural, especially keeping them further away from
            # each other
            boid.acceleration = boid.alignment(other_boids) * 1 + \
                                boid.cohesion(other_boids) * 1 + \
                                boid.separation(other_boids)
        # because we operate on a snapshot of time we only update them at the end.
        for boid in self.boids:
            boid.update()
            self.draw_polygon(self.translate(boid.points, boid.position), color=(51, 51, 51))
            # drawing a line to show a boids velocity and thereby its heading.
            self.draw_line(boid.position, boid.position + boid.velocity * 10, color=(255, 0, 0))

        set_data(self.data)

    def draw_polygon(self, points, color=(255, 0, 255)):
        out = polygon(points[:, 0], points[:, 1])
        self.data[out[0] % (self.res[0] - 1), out[1] % (self.res[1] - 1)] = color

    @staticmethod
    def translate(a, b):
        return a + b

    def draw_line(self, x0y0, x1y1, color=(255, 0, 255)):
        # because Bresenham's line algorithm only works for integers we cast to int
        x0y0 = x0y0.astype(int)
        x1y1 = x1y1.astype(int)
        out = line(
            x0y0[0],
            x0y0[1],
            x1y1[0],
            x1y1[1]
        )
        # wrap around out toroidal world
        self.data[out[0] % (self.res[0] - 1), out[1] % (self.res[1] - 1)] = color


class Boid:
    """
    As with most artificial life simulations,
    Boids is an example of emergent behavior;
    that is, the complexity of Boids arises from the interaction
    of individual agents (the boids, in this case) adhering to a
    set of simple rules. The rules applied in the simplest Boids world are as follows:

        - separation: steer to avoid crowding local flockmates
        - alignment: steer towards the average heading of local flockmates
        - cohesion: steer to move towards the average position (center of mass) of local flockmates
    """

    def __init__(self, pos, vel, acceleration, walls, scale=1, view_radius=50):

        self.points = np.array([(- 1, - 1), (-1, 1), (+ 1, 1), (1, -1)])

        self.position = pos
        self.velocity = vel
        self.acceleration = acceleration
        self.walls = walls
        self.scale = 1
        self.view_radius = view_radius

        self.max_steering_force = .4
        # don't allow the boid to go faster than its initial speed
        self.max_speed = np.linalg.norm(self.velocity)

        self.set_sale(scale)

    def set_sale(self, new):
        self.scale = new
        self.points *= self.scale

    def update(self):
        self.position += self.velocity
        self.position = self.position % self.walls  # wrap around out toroidal world
        self.velocity += self.acceleration

        # limit our speed
        mag = np.linalg.norm(self.velocity)
        if mag > self.max_speed or mag < 1:
            self.velocity = self.velocity / mag * self.max_speed

    def separation(self, boids):
        # avoid collisions
        steering_vel = np.zeros(2)
        total = 0

        for boid in boids:
            if boid != self:
                diff = self.position - boid.position
                diff *= 1 / np.power(np.linalg.norm(self.position - boid.position), 2) * 5
                steering_vel += diff
                total += 1

        if total > 0:
            steering_vel /= total
        else:
            return steering_vel

        steering_vel *= self.max_speed

        if np.linalg.norm(steering_vel) > self.max_steering_force:
            steering_vel = normalize(steering_vel) * self.max_steering_force

        return steering_vel

    def alignment(self, boids):
        # align with other boids
        steering_vel = np.zeros(2)
        total = 0

        for boid in boids:
            if boid != self:
                steering_vel += boid.velocity
                total += 1

        if total > 0:
            steering_vel /= total
        else:
            return steering_vel

        steering_vel *= self.max_speed
        steering_vel -= self.velocity

        if np.linalg.norm(steering_vel) > self.max_steering_force:
            steering_vel = normalize(steering_vel) * self.max_steering_force

        return steering_vel

    def cohesion(self, boids):
        # steer to the center of nearby boids
        steering_vel = np.zeros(2)
        total = 0
        for boid in boids:
            if boid != self:
                steering_vel += boid.position
                total += 1

        if total > 0:
            steering_vel /= total
        else:
            return steering_vel

        steering_vel -= self.position
        steering_vel *= self.max_speed
        steering_vel -= self.velocity

        if np.linalg.norm(steering_vel) > self.max_steering_force:
            steering_vel = normalize(steering_vel) * self.max_steering_force

        return steering_vel


if __name__ == "__main__":
    sim = BoidSimulation(n=100)
    Window.size = (700, 700)
    sim.run()
