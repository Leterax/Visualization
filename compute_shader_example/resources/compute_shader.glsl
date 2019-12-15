// %VARIABLE% will be replaced with consts by python code

#version 430
#define GROUP_SIZE 0//%COMPUTE_SIZE%

layout(local_size_x=GROUP_SIZE) in;

// our balls have a position, velocity and color
struct Ball
{
    vec4 pos;
    vec4 vel;
    vec4 col;
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

    vec4 p = in_ball.pos.xyzw;
    vec4 v = in_ball.vel.xyzw;
    // update its position based on its velocity
    p.xy += v.xy;

    float rad = p.w * 0.5;

    // bounce of all the walls
    if (p.x - rad <= -1.0)
    {
        p.x = -1.0 + rad;
        v.x *= -0.98;
    }
    else if (p.x + rad >= 1.0)
    {
        p.x = 1.0 - rad;
        v.x *= -0.98;
    }
    if (p.y - rad <= -1.0)
    {
        p.y = -1.0 + rad;
        v.y *= -0.98;
    }
    else if (p.y + rad >= 1.0)
    {
        p.y = 1.0 - rad;
        v.y *= -0.98;
    }
    if (p.z - rad <= -1.0)
    {
        p.z = -1.0 + rad;
        v.z *= -0.98;
    }
    else if (p.z + rad >= 1.0)
    {
        p.z = 1.0 - rad;
        v.z *= -0.98;
    }

    // slight dampening on the y-axis
    v.y += -0.001;

    // output the ball into 'Out' with the same values as the in ball
    Ball out_ball;
    out_ball.pos.xyzw = p.xyzw;
    out_ball.vel.xyzw = v.xyzw;
    vec4 c = in_ball.col.xyzw;
    out_ball.col.xyzw = c.xyzw;

    Out.balls[x] = out_ball;
}