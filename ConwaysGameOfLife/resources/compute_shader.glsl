// %VARIABLE% will be replaced with consts by python code

#version 430
#define GROUP_SIZE 0//%COMPUTE_SIZE%

const ivec2 offset = ivec2(-1, -1);

void retirePhase() { memoryBarrierShared(); barrier(); }

layout(local_size_x=3,local_size_y=3) in;
// input from the buffer bound to 0
layout(binding=0, rg32f) uniform image2D input_image;
// output into the buffer bound to 1
layout(binding=1, rg32f) uniform image2D output_image;

shared vec4 pixel[3][3];

void main()
{
  const ivec2 tile_xy = ivec2(gl_WorkGroupID);
  const ivec2 thread_xy = ivec2(gl_LocalInvocationID);

  const uint x = thread_xy.x;
  const uint y = thread_xy.y;

  // Phase 1: Read the image's neighborhood into shared pixel arrays.
  for (int j=0; j<3; j++) {
    for (int i=0; i<3; i++) {
      ivec2 read_at = ivec2(x+i, y+j) + offset;
      pixel[y+j][x+i] = imageLoad(input_image, read_at);
    }
  }
  retirePhase();
  // Phase 2: Compute general convolution.
  vec4 result = vec4(0);
  for (int j=0; j<3; j++) {
    for (int i=0; i<3; i++) {
      result += pixel[y+j][x+i];
    }
  }
  // Phase 3: Store result to output image.
  imageStore(output_image, thread_xy, vec4(0));
}