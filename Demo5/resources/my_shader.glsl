#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_velocity;
out vec2 out_position;
out vec2 out_velocity;

void main() {
    vec2 pos = mod((in_position+in_velocity/2.)+vec2(1.,1.), 2.) - vec2(1.,1.);
    out_position = pos;
    out_velocity = in_velocity;
}

    #endif

