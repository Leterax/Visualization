#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_velocity;
in vec2 in_acceleration;

uniform sampler2D texture0;

const int view = 10;


out vec2 pos;
out vec2 vel;
out vec2 acc;

void main() {

    float max_speed = length(in_velocity);

    vec2 steering_vel;
    float total = 0.;

    ivec2 bpos = ivec2(in_position);

    for (int x = bpos.x - view / 2; x < view; x++){
        for (int y = bpos.y - view / 2; y < view; y++){
            vec4 info = texelFetch(texture0, ivec2(x, y), 0);
            if ((info != vec4(0.)) && (vec2(x, y) != vec2(0))){
                steering_vel += info.xy;
                total += 1.;
            }
        }
    }

    if (total > 0.){
        steering_vel /= total;
    }

    //steering_vel *= max_speed;
    //steering_vel -= in_velocity;

    if (length(steering_vel) > 0.0001){
        steering_vel = normalize(steering_vel)*0.0001;
    }




    pos = in_position;
    vel = in_velocity;
    acc = steering_vel;

    gl_Position = vec4(in_position, 0.0, 1.0);
}

    #endif