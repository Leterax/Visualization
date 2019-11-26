import numpy as np
from PIL import ImageFont
from scipy.ndimage import convolve
from scipy.spatial import cKDTree


class Particle:
    def __init__(self, x, y, color, ball_size=1):
        self.pos = np.array([x, y]).astype(float)
        self.vel = np.zeros(2)
        self.acc = np.zeros(2)

        self.target = self.pos

        self.radius = ball_size

        self.max_speed = 10
        self.max_force = .6

        self.color = np.array(color, dtype=np.uint8)

    def update(self):
        self.pos += self.vel
        self.vel += self.acc

        self.acc *= 0

    def arrive(self):
        # calculate the distance
        dist = np.linalg.norm(self.target - self.pos)
        # normalize it
        desired = (self.target - self.pos) / dist

        # if we are less than 100px away from our target, start to slow down
        if dist < 100:
            speed = dist / 100 * self.max_speed
        else:
            # otherwise go at full speed
            speed = self.max_speed

        # set the magnitude of our desired vector
        desired *= speed

        steer = desired - self.vel

        steer_mag = np.linalg.norm(steer)
        if steer_mag > self.max_force:
            steer = steer / steer_mag * self.max_force
        return steer


def render_text_perimeter_balls(txt, pos=(0, 0), scale=16, color=(235, 64, 52), ball_size=4.5):
    # place particles on the text outline without overlapping them.
    font = ImageFont.truetype(r"resources\VCR_OSD_MONO_1.001.ttf", scale)
    a = font.getmask(txt)
    out = np.empty(a.size)
    for y in range(a.size[0]):
        for x in range(a.size[1]):
            out[y, x] = a.getpixel((y, x))

    out = out / 255
    out = np.where(out > 0, 1, 0)
    out = np.rot90(out)

    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    out = convolve(out, kernel, mode='constant')
    outline = np.where(out == 5, 1, 0)
    indices = np.transpose(outline.nonzero()) + np.array(pos)

    particles = []

    for xy in indices:
        particles.append(Particle(xy[1], xy[0], color, ball_size))

    quadTree = cKDTree([p.pos for p in particles])

    # loop over particles. remove all touching particles
    to_remove = set()
    for particle in particles:
        if particle in to_remove: continue
        colliding_particles = [particles[i] for i in quadTree.query_ball_point(particle.pos, particle.radius * 2)]
        for p in colliding_particles:
            if p != particle:
                to_remove.add(p)

    for particle in to_remove:
        particles.remove(particle)

    out = np.array([p.pos for p in particles])
    # out = out/np.linalg.norm(out)
    return out


if __name__ == "__main__":
    # generate the particles with their target position
    render_text_perimeter_balls("Hey!", scale=300, pos=(75, 250), color=(226, 53, 31))
    render_text_perimeter_balls("#show-your-projects", scale=70, pos=(10, 150), color=(231, 201, 49), ball_size=2)
