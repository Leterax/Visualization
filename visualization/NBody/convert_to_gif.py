import os
import time
from pathlib import Path

import imageio


class SaveToFile:
    def __init__(self, folder: str, fps: int, file_format: str = "gif") -> None:
        """
        Convert a image sequence to a gif or movie.

        :param folder: folder to read images from. Should be located in the 'screen_recordings' directory
        :param fps: fps to render the movie/gif at
        :param file_format: 'gif' or 'mp4'
        """
        if file_format not in ["gif", "mp4"]:
            raise ValueError("file_format has to be 'gif' or 'mp4'.")
        if fps < 1:
            raise ValueError("fps has to be larger than 1")

        self.folder = folder
        self.fps = fps
        self.file_format = file_format

        self.screenshots_dir = (
            Path(__file__) / f"../screen_recordings/{folder}"
        ).absolute()

        image_sequence = self.read_files()

        if self.file_format == "gif":
            self.save_to_gif(image_sequence)
        elif self.file_format == "mp4":
            self.save_to_video(image_sequence)

        print("Done writing to file.")

    def read_files(self):
        images = []
        all_files = filter(
            lambda f: f.endswith(".png"), os.listdir(self.screenshots_dir)
        )
        print("done collecting files")
        for file in all_files:
            images.append(imageio.imread(self.screenshots_dir / file))

        return images

    def save_to_video(self, images):
        print("writing to mp4")
        writer = imageio.get_writer(f"{self.folder}-{time.time()}.mp4", fps=self.fps)

        for im in images:
            writer.append_data(im)
        writer.close()

    def save_to_gif(self, images):
        print("writing to gif")
        imageio.mimsave(
            f"simulation-{self.folder}-{time.time()}.gif", images, fps=self.fps
        )


file_saver = SaveToFile("uniform100", 30, "gif")
