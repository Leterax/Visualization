from pathlib import Path

import moderngl_window as mglw


class BasicWindowConfig(mglw.WindowConfig):
    """Minimal WindowConfig example"""
    gl_version = (3, 3)
    title = "Basic Window Config"
    resource_dir = Path(__file__).parent.parent.absolute() / 'resources'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render(self, time, frametime):
        pass


if __name__ == '__main__':
    mglw.run_window_config(BasicWindowConfig)

