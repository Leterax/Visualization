#version 330

#if defined VERTEX_SHADER

in int in_prime;
uniform float n;

void main() {
    vec2 polar = vec2(in_prime*cos(in_prime), in_prime*sin(in_prime))/n;
    gl_Position = vec4(polar, 1., 1.0);
}

    #elif defined GEOMETRY_SHADER


layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform float size;
uniform mat4 m_proj;

out vec2 uv;

void main() {
    vec2 pos = gl_in[0].gl_Position.xy;

    vec2 right = vec2(1.0, 0.0) * size;
    vec2 up = vec2(0.0, 1.0) * size;

    uv = vec2(1.0, 1.0);
    gl_Position = vec4(pos + (right + up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(0.0, 1.0);
    gl_Position = vec4(pos + (-right + up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(1.0, 0.0);
    gl_Position = vec4(pos + (right - up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(0.0, 0.0);
    gl_Position = vec4(pos + (-right - up), 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}

    #elif defined FRAGMENT_SHADER

out vec4 fragColor;
in vec2 uv;

uniform vec3 color;


void main() {
    vec2 pos = uv - vec2(0.5, 0.5);
    float len = step(0.0, 0.5 - length(pos));
    fragColor = vec4(color*len, len);
}


    #endif

