from pathlib import Path

import moderngl

import moderngl_window as mglw
from moderngl_window.opengl.vao import VAO

import numpy as np


def primes_from2to(n: int) -> np.ndarray:
    """Input n>=6, Returns a array of primes, 2 <= p < n."""
    sieve = np.ones(n // 3 + (n % 6 == 2), dtype=np.bool)
    for i in range(1, int(n ** 0.5) // 3 + 1):
        if sieve[i]:
            k = 3 * i + 1 | 1
            sieve[k * k // 3 :: 2 * k] = False
            sieve[k * (k - 2 * (i & 1) + 4) // 3 :: 2 * k] = False
    return np.r_[2, 3, ((3 * np.nonzero(sieve)[0][1:] + 1) | 1)]


def f(x: float, b: float = 3.0) -> float:
    return np.sqrt((1 + b ** 2) / (1 + b ** 2 * np.sin(x) ** 2)) * np.sin(x)


class PolarPrimes(mglw.WindowConfig):
    """Render prime numbers in polar coordinates."""

    gl_version = (3, 3)
    title = "PolarPrimes"
    samples = 16
    window_size = 720, 720
    aspect_ratio = 1
    resizable = False
    resource_dir = Path(__file__).parent.joinpath("resources").resolve()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.program = self.load_program("primes_shader.glsl")

        self.program["color"].value = (191 / 255, 67 / 255, 69 / 255)
        self.program["size"].value = 0.005
        self.zoom = 100
        self.n = 2 ** 25
        self.program["n"].value = self.n
        primes = primes_from2to(self.n)

        self.buffer = self.ctx.buffer(primes)
        self.vao1 = VAO(name="boids_1")
        self.vao1.buffer(self.buffer, "1i", ["in_prime"])

    def render(self, time: float, frame_time: float) -> None:
        r = g = b = 51 / 255
        self.ctx.clear(r, g, b)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.program["n"].value = max((-f(time / 2 ** 3) + 1) / 2 * self.n, 2000)

        self.vao1.render(self.program, mode=moderngl.POINTS)

    def key_event(self, key: str, action: str, modifiers: str) -> None:
        keys = self.wnd.keys

        if action == keys.ACTION_PRESS:
            if key == keys.SPACE:
                self.timer.toggle_pause()


if __name__ == "__main__":
    PolarPrimes.run()
