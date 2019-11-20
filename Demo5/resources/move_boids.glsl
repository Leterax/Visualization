#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_velocity;
in vec2 in_acceleration;
out vec2 out_position;
out vec2 out_velocity;
out vec2 out_acceleration;


void main() {
    vec2 pos = mod((in_position+in_velocity)+vec2(1.,1.), 2.) - vec2(1.,1.);
    out_position = pos;

    out_velocity = in_velocity + in_acceleration;
    if (length(out_velocity) < 0.001){
        out_velocity = normalize(out_velocity)*0.005;
    }
    out_acceleration = vec2(0.);
}

    #endif

