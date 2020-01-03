// %VARIABLE% will be replaced with consts by python code

#version 430
#define GROUP_SIZE 0//%COMPUTE_SIZE%

#define N 0//%N%
#define G 6.67408e-11
#define E 0//%E%


layout(local_size_x=GROUP_SIZE) in;

// our Planets have a position, velocity and color
struct Planet
{
    vec4 pos;
    vec4 vel;
    vec4 frc;
    vec4 col;
};

// input from the buffer bound to 0
layout(std430, binding=0) buffer planets_in
{
    Planet planets[];
} In;

// output into the buffer bound to 1
layout(std430, binding=1) buffer planets_out
{
    Planet planets[];
} Out;

void main()
{
    // get the current position
    int x = int(gl_GlobalInvocationID);
    // get the current Planet we want to look at
    Planet in_planet = In.planets[x];

    vec3 p = in_planet.pos.xyz;
    vec3 v = in_planet.vel.xyz;
    vec3 f = in_planet.frc.xyz;
    float m = in_planet.vel.w;

    vec3 f_i = vec3(0.);
    for (int i=0; i <= N; i++){
        Planet j = In.planets[i];
        if (j!=in_planet){
            if (length(p-j.pos.xyz) > 0.001){
                vec3 top = G * m * j.vel.w * (p-j.pos.xyz);
                float bottom = length(p-j.pos.xyz);
                bottom = bottom*bottom*bottom;
                f_i += top/bottom;
            }
        }
    }


    // output the Planet into 'Out' with the same values as the in Planet
    Planet out_planet;
    out_planet.pos.xyzw = in_planet.pos;
    out_planet.vel.xyzw = in_planet.vel;
    out_planet.col = in_planet.col;
    out_planet.frc = vec4(-f_i, 1.);

    Out.planets[x] = out_planet;
}