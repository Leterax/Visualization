import os, re
import time

SETTINGS = ""


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_programs():
    folders = [
        name
        for name in os.listdir("./visualization/")
        if os.path.isdir("./visualization/" + name)
    ]
    apps = [
        "_".join(s.lower() for s in name) + ".py"
        for name in (re.findall("[A-Z][^A-Z]*", folder) for folder in folders)
    ]
    print(*[f"[{i}]: {name}\n" for i, name in enumerate(apps)], sep="")

    choice = input("> ")
    if choice not in {str(x) for x in range(len(apps))}:
        return
    choice = int(choice)
    print(
        f"launching 'python visualization/{folders[choice]}/{apps[choice]} {SETTINGS}".strip(
            " "
        )
        + "'"
    )
    os.system(
        f"python visualization/{folders[choice]}/{apps[choice]} {SETTINGS}".strip(" ")
    )


def print_settings():
    print(
        """optional arguments:
  -wnd {glfw,headless,pygame2,pyglet,pyqt5,pyside2,sdl2,tk}, --window {glfw,headless,pygame2,pyglet,pyqt5,pyside2,sdl2,tk}
                        Name for the window type to use
  -fs, --fullscreen     Open the window in fullscreen mode
  -vs VSYNC, --vsync VSYNC
                        Enable or disable vsync
  -r RESIZABLE, --resizable RESIZABLE
                        Enable/disable window resize
  -s SAMPLES, --samples SAMPLES
                        Specify the desired number of samples to use for
                        multisampling
  -c CURSOR, --cursor CURSOR
                        Enable or disable displaying the mouse cursor
  --size SIZE           Window size
  --size_mult SIZE_MULT
                        Multiplier for the window size making it easy scale
                        the window
"""
    )
    global SETTINGS
    SETTINGS = input("> ")


user_input = ""
while user_input not in {"q", "exit", "quit"}:
    clear()
    user_input = input("launch ['l'], settings ['s'], quit ['q']\n> ").lower()
    if user_input == "l":
        # launch a application
        clear()
        print_programs()

    if user_input == "s":
        # show settings
        clear()
        print_settings()
