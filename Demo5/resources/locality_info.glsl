#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_velocity;
in vec2 in_acceleration;

uniform sampler2D texture0;

const int view = 50;


out vec2 pos;
out vec2 vel;
out vec2 acc;

void main() {

    float max_speed = length(in_velocity);

    vec2 result;

    vec2 steering_vel_allign;
    //vec2 steering_vel_cohesion;

    float total = 0.;

    ivec2 bpos = ivec2(in_position);

    for (int x = bpos.x - view / 2; x < bpos.x + view / 2; x++){
        for (int y = bpos.y - view / 2; y < bpos.y + view / 2; y++){
            vec4 info = texelFetch(texture0, ivec2(x, y), 0);
            if (info.x>0.001 || info.y>0.001 || info.z>0.001 || info.w>0.001){
                vec2 diff = in_position - info.xy;
                steering_vel_allign += (1/ length(diff)) * info.zw;
                //steering_vel_cohesion += info.zw;
                total += 1.;
            }
        }
    }

    if (total > 0.){
        steering_vel_allign /= total;

        steering_vel_allign -= in_velocity;


        if (length(steering_vel_allign) > .4){
            steering_vel_allign = normalize(steering_vel_allign)* .4;
        }
//        steering_vel_allign *= max_speed;
    }
    else {
        steering_vel_allign = vec2(0.);
    }




    result = steering_vel_allign;

    pos = in_position;
    vel = in_velocity;
    acc = result;

    //gl_Position = vec4(in_position, 0.0, 1.0);
}

    #endif