// %VARIABLE% will be replaced with consts by python code

#version 430
#define GROUP_SIZE 0//%COMPUTE_SIZE%
#define DT 0//%DT%

layout(local_size_x=GROUP_SIZE) in;

// our Planets have a position, velocity and color
struct Planet
{
    dvec4 pos;
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

    dvec3 p = in_planet.pos.xyz;
    vec3 v = in_planet.vel.xyz;
    vec3 f = in_planet.frc.xyz;
    float m = in_planet.vel.w;

    // F = m*a
    // F/m = a
    // v = a*dt
    // s = v*dt

    vec3 new_a = f/m*DT;
    vec3 new_v = v + new_a*DT;
    dvec3 new_p = p + new_v*DT;


    // output the Planet into 'Out' with the same values as the in Planet
    Planet out_planet;
    out_planet.pos.xyzw = dvec4(new_p, 1.);
    out_planet.vel.xyzw = vec4(new_v, 1.);
    out_planet.col = in_planet.col;
    out_planet.vel.w = in_planet.vel.w;
    out_planet.frc = in_planet.frc;
    Out.planets[x] = out_planet;
}