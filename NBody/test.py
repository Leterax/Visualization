import os

import imageio  # for output
import moderngl
import numpy as np

# W = X * Y  // for each run, handles a row of pixels
# execute compute shader for H times to complete
W = 512
H = 256
X = W
Y = 1
Z = 1
consts = {
    "W": W,
    "H": H,
    "X": X + 1,
    "Y": Y,
    "Z": Z,
}

FRAMES = 50
SOURCE_PATH = os.path.dirname(__file__)
OUTPUT_DIRPATH = os.path.join(SOURCE_PATH, "output")

if not os.path.isdir(OUTPUT_DIRPATH):
    os.makedirs(OUTPUT_DIRPATH)

glsl_file = os.path.join(SOURCE_PATH, 'gl/median_5x5.gl')
context = moderngl.create_standalone_context(require=430)
compute_shader = context.compute_shader(source(glsl_file, consts))

# init buffers
buffer_a_data = np.random.uniform(0.0, 1.0, (H, W, 4)).astype('f4')
buffer_a = context.buffer(buffer_a_data)
buffer_b_data = np.zeros((H, W, 4)).astype('f4')
buffer_b = context.buffer(buffer_b_data)

imgs = []
last_buffer = buffer_b
for i in range(FRAMES):
    toggle = True if i % 2 else False
    buffer_a.bind_to_storage_buffer(1 if toggle else 0)
    buffer_b.bind_to_storage_buffer(0 if toggle else 1)

    # toggle 2 buffers as input and output
    last_buffer = buffer_a if toggle else buffer_b

    # local invocation id x -> pixel x
    # work groupid x -> pixel y
    # eg) buffer[x, y] = gl_LocalInvocationID.x + gl_WorkGroupID.x * W
    compute_shader.run(group_x=H, group_y=1)

    # print out
    output = np.frombuffer(last_buffer.read(), dtype=np.float32)
    output = output.reshape((H, W, 4))
    output = np.multiply(output, 255).astype(np.uint8)
    imgs.append(output)

# if you don't want to use imageio, remove this section
out_path = f"{OUTPUT_DIRPATH}/debug.gif"
print("Writing GIF anim to", out_path)
imageio.mimwrite(out_path, imgs, "GIF", duration=0.15)
