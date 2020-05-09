#version 330

#if defined VERTEX_SHADER

in vec2 in_position;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
}

#elif defined FRAGMENT_SHADER

#define SEED_COUNT 4096

layout(pixel_center_integer) in vec4 gl_FragCoord;

out vec4 fragColor;

uniform vec2 iResolution;
uniform mat4 m_projection;

uniform float time;

layout (std140) uniform Seeds {
    vec2 values[SEED_COUNT];
} seeds;

layout (std140) uniform Colors {
    vec3 values[SEED_COUNT];
} seed_colors;

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution;

    vec2 gv = fract(uv)-.5;


    float min_dist = 100.*100.;
    int min_index = 0;
    for (int i = 0; i < SEED_COUNT; i++){
        vec2 dst = uv - seeds.values[i];
        float sq_dst = dot(dst, dst);
        if (sq_dst < min_dist){
            min_dist = sq_dst;
            min_index = i;
        }
    }

    fragColor = vec4(seed_colors.values[min_index], 1);
}
#endif