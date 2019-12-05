#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_velocity;
in vec2 in_acceleration;

uniform sampler2D texture0;

const int view = 300;


out vec2 pos;
out vec2 vel;
out vec2 acc;

vec2 dst(vec2 a, vec2 b){

    //sqrt(min(|x1 - x2|, w - |x1 - x2|)^2 + min(|y1 - y2|, h - |y1 - y2|)^2)
    // (min(abs(x1 - x2), w - abs(x1 - x2)), min(abs(y1 - y2), h - abs(y1 - y2)))

    float h = 1.;
    float w = 1.;
    return vec2(min(abs(a.x-b.x), w- abs(a.x-b.x)), min(abs(a.y-b.y), h-abs(a.y-b.y)));

}


bool isNotBlack (vec4 data) {
    return (data.x>0.001 || data.y>0.001 || data.z>0.001 || data.w>0.001);
}

void main() {
    vec2 result = vec2(0.);
    vec2 steering_vel_seperation;
    float total = 0.;
    // shift in_position from -100,100 to range 0,200 then scale to texture size
    ivec2 bpos = ivec2(
    (vec2(in_position) + vec2(1.)) / 2.0 * vec2(textureSize(texture0, 0))
    );

    for (int x = bpos.x - view / 2; x < bpos.x + view / 2; x++){
        for (int y = bpos.y - view / 2; y < bpos.y + view / 2; y++){

            ivec2 texpos = ivec2(mod(vec2(x, y), textureSize(texture0, 0)));
            vec4 info = texelFetch(texture0, texpos, 0);

            if (isNotBlack(info)){
                // shift to 0-1 space
                vec2 a = in_position/2.+vec2(1.);
                vec2 b = info.zw/2.+vec2(1.);
                float diff = length(dst(a, b));
                if (diff < view){
                    if (diff > 1e-6){
                        steering_vel_seperation += (1. / diff) * (dst(a, b));
                        total += 1.;
                    }
                }
            }
        }
    }

    if (total > 0.){
        steering_vel_seperation /= total;
        steering_vel_seperation *= 2.;
        steering_vel_seperation -= 1.;


        steering_vel_seperation -= in_velocity;

        if (length(steering_vel_seperation) > .00375){
            steering_vel_seperation = normalize(steering_vel_seperation) * .00375;
        }
    }
    else {
        steering_vel_seperation = vec2(0.);
    }




    result = steering_vel_seperation;

    pos = in_position;
    vel = in_velocity;
    acc = result;

}

    #endif