#version 410

#if defined VERTEX_SHADER

in vec2 in_position;


void main() {
    gl_Position = vec4(in_position/100., 0., 1.);
}


    #elif defined GEOMETRY_SHADER

layout (points) in;
layout (triangle_strip, max_vertices = 8) out;

in int gl_PrimitiveIDIn;
out int gl_PrimitiveID;


uniform sampler2D texture0;

void main() {

    vec2 pos = gl_in[0].gl_Position.xy;


    vec2 size = vec2(.1) / textureSize(texture0, 0) / 2.;

    vec2 bottom_left = pos - size;
    vec2 bottom_right = pos + vec2(size.x, -size.y);
    vec2 top_right = pos + size;
    vec2 top_left = pos + vec2(-size.x, size.y);



    gl_PrimitiveID = gl_PrimitiveIDIn;
    gl_Position = vec4(bottom_left, 0.0, 1.0);
    EmitVertex();

    gl_PrimitiveID = gl_PrimitiveIDIn;
    gl_Position = vec4(bottom_right, 0.0, 1.0);
    EmitVertex();

    gl_PrimitiveID = gl_PrimitiveIDIn;
    gl_Position = vec4(top_left, 0.0, 1.0);
    EmitVertex();

    gl_PrimitiveID = gl_PrimitiveIDIn;
    gl_Position = vec4(top_right, 0.0, 1.0);
    EmitVertex();

    EndPrimitive();

    bool extra_quad = false;

    if (mod(bottom_left+vec2(1.), 2.) != bottom_left+vec2(1.) && mod(top_left+vec2(1.), 2.) != top_left+vec2(1.)){
        bottom_left = mod(bottom_left+vec2(1.), 2.) -1.;
        top_left = mod(top_left+vec2(1.), 2.) -1.;
        bottom_right = vec2(1., bottom_right.y);
        top_right = vec2(1., top_right.y);

        extra_quad = true;
    }
    if (mod(bottom_right+vec2(1.), 2.) != bottom_right+vec2(1.) && mod(top_right+vec2(1.), 2.) != top_right+vec2(1.)){
        bottom_right = mod(bottom_right+vec2(1.), 2.) -1.;
        top_right = mod(top_right+vec2(1.), 2.) -1.;
        bottom_left = vec2(-1., bottom_left.y);
        top_left = vec2(-1., top_left.y);

        extra_quad = true;
    }


    if (mod(top_left+vec2(1.), 2.) != top_left+vec2(1.) && mod(top_right+vec2(1.), 2.) != top_right+vec2(1.)){
        top_left = mod(top_left+vec2(1.), 2.) -1.;
        top_right = mod(top_right+vec2(1.), 2.) -1.;
        bottom_right = vec2(bottom_right.x, -1.);
        bottom_left = vec2(top_right.x, -1.);

        extra_quad = true;
    }
    if (mod(bottom_left+vec2(1.), 2.) != bottom_left+vec2(1.) && mod(bottom_right+vec2(1.), 2.) != bottom_right+vec2(1.)){
        bottom_left = mod(bottom_left+vec2(1.), 2.) -1.;
        bottom_right = mod(bottom_right+vec2(1.), 2.) -1.;
        top_right = vec2(top_right.x, 1.);
        top_left = vec2(top_left.x, 1.);

        extra_quad = true;
    }

    if (extra_quad){
        gl_PrimitiveID = gl_PrimitiveIDIn;
        gl_Position = vec4(bottom_left, 0.0, 1.0);
        EmitVertex();

        gl_PrimitiveID = gl_PrimitiveIDIn;
        gl_Position = vec4(bottom_right, 0.0, 1.0);
        EmitVertex();

        gl_PrimitiveID = gl_PrimitiveIDIn;
        gl_Position = vec4(top_left, 0.0, 1.0);
        EmitVertex();

        gl_PrimitiveID = gl_PrimitiveIDIn;
        gl_Position = vec4(top_right, 0.0, 1.0);
        EmitVertex();

        EndPrimitive();
    }

}

    #elif defined FRAGMENT_SHADER

out vec4 fragColor;
in int gl_PrimitiveID;
uniform int num_boids;

// 360°, 50%, 70%
vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}


void main() {
    //float index = float(gl_PrimitiveID)/float(num_boids);
    //vec3 color = hsv2rgb(vec3(index, .5, .7));
    fragColor = vec4(0.18, 0.18, 0.18, .5);


}


    #endif

