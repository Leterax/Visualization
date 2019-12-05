#version 330

#if defined VERTEX_SHADER
#define SMALL 0.0001
in vec2 in_position;
in vec2 in_velocity;
in vec2 in_acceleration;
out vec2 out_position;
out vec2 out_velocity;
out vec2 out_acceleration;


void main() {
    vec2 pos = mod((in_position+in_velocity)+vec2(1., 1.), vec2(2.)) - vec2(1., 1.);

    vec2 acceleration = in_acceleration;
    //if (isnan(acceleration.x)) { acceleration.x = 0.; }
    //if (isnan(acceleration.y)) { acceleration.y = 0.; }


    vec2 updated_velocity = in_velocity + acceleration;
    if (length(updated_velocity) > 0.00375){
        updated_velocity = normalize(updated_velocity) * 0.00375;
    }

    out_position = pos;
    out_velocity = updated_velocity;
    out_acceleration = vec2(0.);
}

    #endif

