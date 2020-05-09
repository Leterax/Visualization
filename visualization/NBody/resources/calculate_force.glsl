#version 430

#define GROUP_SIZE 64
#define DT 60*60*24
#define N 50

const double G = 3.9640159924573524e-14;


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


    dvec3 f_i = vec3(0.);

    for (int i=0; i <= N; i++){
        Planet j = In.planets[i];
        if (j!=in_planet){
            dvec3 other_pos = dvec3(j.px, j.py, j.pz);
            dvec3 dst_vec = p-other_pos;
            double len = length(dst_vec);
            if (len > 0.001){
                dvec3 top = G * in_planet.mass * j.mass * dst_vec;
                double bottom = len*len*len;

                f_i += dvec3(top/bottom);
            }
        }
    }
    f_i = -1.*f_i;
    // output the Planet into 'Out' with the same values as the in Planet
    Planet out_planet = Planet(p.x,   p.y,   p.z,
                               v.x,   v.y,   v.z,
                               f_i.x, f_i.y, f_i.z,
                               m);

    Out.planets[x] = out_planet;
}