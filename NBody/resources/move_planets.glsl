// %VARIABLE% will be replaced with consts by python code

#version 430
#define GROUP_SIZE 0//%COMPUTE_SIZE%
#define _DT 0//%DT%lf

layout(local_size_x=GROUP_SIZE) in;

// our Planets have a position, velocity and color
struct Planet
{
    dvec3 pos;
    dvec3 vel;
    dvec3 frc;
    float mass;
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

    dvec3 p = in_planet.pos;
    dvec3 v = in_planet.vel;
    dvec3 f = in_planet.frc;
    double m = double(in_planet.mass);

    // F = m*a
    // F/m = a
    // v = a*dt
    // s = v*dt

    dvec3 new_a = (f/m)*DT;
    dvec3 new_v = v + new_a*DT;
    dvec3 new_p = p + new_v*DT;


    // output the Planet into 'Out' with the same values as the in Planet
    Planet out_planet = Planet(new_p, new_v, in_planet.frc, in_planet.mass, in_planet.col);


    Out.planets[x] = out_planet;
}