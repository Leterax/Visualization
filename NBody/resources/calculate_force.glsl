// %VARIABLE% will be replaced with consts by python code

#version 430
#define GROUP_SIZE 0//%COMPUTE_SIZE%

#define N 0//%N%
#define G 6.67408e-11


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

    dvec3 f_i = vec3(0.);

    for (int i=0; i <= N; i++){
        Planet j = In.planets[i];
        if (j!=in_planet){
            dvec3 dst_vec = in_planet.pos.xyz-j.pos;

            if (length(dst_vec) > 0.001){
                dvec3 top = G * in_planet.mass * j.mass * dst_vec;
                double bottom = length(dst_vec);

                bottom = bottom*bottom*bottom;

                f_i += dvec3(top/bottom);
            }
        }
    }

    f_i = dvec3(1, 2, 3);
    // output the Planet into 'Out' with the same values as the in Planet
    Planet out_planet = Planet(in_planet.pos, in_planet.vel, in_planet.frc, in_planet.mass, in_planet.col);

    Out.planets[x] = out_planet;
}