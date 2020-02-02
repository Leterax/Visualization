// %VARIABLE% will be replaced with consts by python code

#version 430
#define KERNEL_SIZE 3

#define LIVING 1.0
#define DEAD 0.0

const ivec2 offset = ivec2(-KERNEL_SIZE/2, -KERNEL_SIZE/2);

void retirePhase() { memoryBarrierShared(); barrier(); }

layout(local_size_x=KERNEL_SIZE, local_size_y=KERNEL_SIZE) in;
// input from the buffer bound to 0
layout(binding=0, rgba8) uniform image2D input_image;
// output into the buffer bound to 1
layout(binding=1, rgba8) uniform image2D output_image;

const ivec2 image_size = ivec2(imageSize(input_image));

ivec2 wrap(ivec2 p){
  return ivec2(mod(p, image_size));
}

void main()
{
    // use a kernel to get the average color of the sourounding pixels
    vec4 pixel[KERNEL_SIZE][KERNEL_SIZE];

    const ivec2 pixel_xy = ivec2(gl_GlobalInvocationID.xy);
    const int x = pixel_xy.x;
    const int y = pixel_xy.y;
    // Phase 1: Read the image's neighborhood into shared pixel arrays.
    for (int j=0; j<KERNEL_SIZE; j++) {
        for (int i=0; i<KERNEL_SIZE; i++) {
            ivec2 read_at = ivec2(x+i, y+j) + offset;
            pixel[j][i] = imageLoad(input_image, wrap(read_at));
        }
    }

    //Phase 2: Compute general convolution.
    int neighbours = 0;
    for (int j=0; j<KERNEL_SIZE; j++) {
        for (int i=0; i<KERNEL_SIZE; i++) {
            if (i==1 && j==1){ }
            else { neighbours += int(pixel[j][i].a); }

        }
    }
    //Phase 3: Apply GoL rules
    //Phase 4: Store result to output image.
    bool cell_alive = imageLoad(input_image, pixel_xy).a > .5;
    float next_value;
    if (cell_alive){
        next_value = (neighbours == 2 || neighbours == 3) ? LIVING : DEAD;
    } else {
        next_value = (neighbours == 3) ? LIVING : DEAD;
    }

    imageStore(output_image, pixel_xy, vec4(0.1176, 0.9215,  0.1882, next_value));
}
