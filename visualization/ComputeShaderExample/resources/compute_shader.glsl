#version 430

#define GROUP_SIZE 0
#define BALL_SIZE 0
#define BOX_SIZE 0

layout(local_size_x=GROUP_SIZE) in;

// our balls have a position, velocity and color
struct Ball
{
    float posx; float posy; float posz;
    float velx; float vely; float velz;
};

// input from the buffer bound to 0
layout(std430, binding=0) buffer balls_in
{
    Ball balls[];
} In;

// output into the buffer bound to 1
layout(std430, binding=1) buffer balls_out
{
    Ball balls[];
} Out;

void main()
{
    // get the current position
    int x = int(gl_GlobalInvocationID);
    // get the current ball we want to look at
    Ball in_ball = In.balls[x];

    vec3 p = vec3(in_ball.posx, in_ball.posy, in_ball.posz);
    vec3 v = vec3(in_ball.velx, in_ball.vely, in_ball.velz);
    // update its position based on its velocity
    p += v;

    // we assume the box is centerd around (0,0,0)
    if (p.x - BALL_SIZE < -BOX_SIZE || p.x + BALL_SIZE > BOX_SIZE){
        v.x *= -.98;
    }
    if (p.y - BALL_SIZE < -BOX_SIZE || p.y + BALL_SIZE > BOX_SIZE){
        v.y *= -.98;
    }

    if (p.z - BALL_SIZE < -BOX_SIZE || p.z + BALL_SIZE > BOX_SIZE){
        v.z *= -.98;
    }

    // output the ball into 'Out' with the same values as the in ball
    Out.balls[x] = Ball(p.x, p.y, p.z,
    v.x, v.y, v.z);
}