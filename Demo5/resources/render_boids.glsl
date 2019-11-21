#version 410

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_velocity;

out vec2 out_velocity;

void main() {
    gl_Position = vec4(in_position/100., 0., 1.);
    out_velocity = normalize(in_velocity);
}


#elif defined GEOMETRY_SHADER

layout (points) in;
layout (triangle_strip, max_vertices = 3) out;

in int gl_PrimitiveIDIn;
out int gl_PrimitiveID;

in vec2 out_velocity[1];
uniform float size;

vec2 rotate(vec2 v, float a) {
	float s = sin(a);
	float c = cos(a);
	mat2 m = mat2(c, -s, s, c);
	return m * v;
}

void main() {

    vec2 pos = gl_in[0].gl_Position.xy;

    float theta = atan(out_velocity[0].x, out_velocity[0].y);


    // generate a triangle centered on `in_position`
    vec2 c1 = vec2(-1., -0.5) * size;
    vec2 c2 = vec2(0., 2.5) * size;
    vec2 c3 = vec2(1., -0.5) * size;


    gl_PrimitiveID = gl_PrimitiveIDIn;
    gl_Position = vec4(pos + rotate(c1, theta), 0.0, 1.0);
    EmitVertex();

    gl_PrimitiveID = gl_PrimitiveIDIn;
    gl_Position = vec4(pos + rotate(c2, theta), 0.0, 1.0);
    EmitVertex();

    gl_PrimitiveID = gl_PrimitiveIDIn;
    gl_Position = vec4(pos + rotate(c3, theta), 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
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
    float index = float(gl_PrimitiveID)/float(num_boids);
    vec3 color = hsv2rgb(vec3(index, .5, .7));
    fragColor = vec4(color, 1.);



}


    #endif

