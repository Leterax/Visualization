#version 430

#define GROUP_SIZE 64
#define DT 60*60*24
#define N 50


layout(local_size_x=GROUP_SIZE) in;

// our Planets have a position, velocity and color
struct Planet
{
    double px, py, pz;
    double vx, vy, vz;
    double fx, fy, fz;
    double mass;
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

    dvec3 p = dvec3(in_planet.px, in_planet.py, in_planet.pz);
    dvec3 v = dvec3(in_planet.vx, in_planet.vy, in_planet.vz);
    dvec3 f = dvec3(in_planet.fx, in_planet.fy, in_planet.fz);
    double m = in_planet.mass;

    dvec3 new_a = (f/m);
    dvec3 new_v = v + new_a*DT;
    dvec3 new_p = p + new_v*DT;


    // output the Planet into 'Out' with the same values as the in Planet
    Planet out_planet = Planet(new_p.x,      new_p.y,      new_p.z,
                               new_v.x,      new_v.y,      new_v.z,
                               in_planet.fx, in_planet.fy, in_planet.fz,
                               in_planet.mass);


    Out.planets[x] = out_planet;
}