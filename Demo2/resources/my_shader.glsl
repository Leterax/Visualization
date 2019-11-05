#version 330

#if defined VERTEX_SHADER

in vec2 in_position;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
}


#elif defined FRAGMENT_SHADER

layout(pixel_center_integer) in vec4 gl_FragCoord;

out vec4 fragColor;

uniform vec2 iResolution;
uniform mat4 m_projection;

uniform float time;

uniform int seed_count;
uniform vec2[100] seeds;
uniform vec3[100] seed_colors;


void main() {
    vec2 uv = gl_FragCoord.xy / iResolution;
    float min_dist = 100.0;
    int min_index = 0;
    for (int i = 0; i < seed_count; i++){
        float dst = distance(uv, seeds[i]);
        if (dst < min_dist){
            min_dist = dst;
            min_index = i;
        }
    }
    fragColor = vec4(seed_colors[min_index], 1);
}
#endif