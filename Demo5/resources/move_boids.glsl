#version 330

#if defined VERTEX_SHADER
#define SMALL 0.01
in vec2 in_position;
in vec2 in_velocity;
in vec2 in_acceleration;
out vec2 out_position;
out vec2 out_velocity;
out vec2 out_acceleration;


void main() {

    vec2 pos = mod((in_position+in_velocity)+vec2(100., 100.), 200.) - vec2(100., 100.);
    vec2 updated_velocity;

    vec2 acceleration = in_acceleration;
    if (isnan(acceleration.x)) { acceleration.x = 0.; }
    if (isnan(acceleration.y)) { acceleration.y = 0.; }



    updated_velocity = in_velocity + acceleration;

    float l = length(updated_velocity);
    if (l < 0.3 && l > SMALL){
        updated_velocity = updated_velocity/l*0.3;
    }
    else if (l > 3.){
        updated_velocity = updated_velocity/l*3.;
    }




    out_position = pos;
    out_velocity = updated_velocity;
    out_acceleration = acceleration;
}

    #endif

