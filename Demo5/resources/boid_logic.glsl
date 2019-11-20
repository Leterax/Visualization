#version 410

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_velocity;

out vec2 out_velocity;

void main() {
    gl_Position = vec4(in_position, 0., 1.);
    out_velocity = in_velocity;
}
    #endif

