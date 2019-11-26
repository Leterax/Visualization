#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 target;

out vec2 vert_target;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    vert_target = target;
}

    #elif defined GEOMETRY_SHADER

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform float time;
uniform mat4 m_proj;
uniform float size;

uniform mat4 model_view;

in vec2 vert_target[1];
out vec2 uv;

void main() {
    vec2 in_position = gl_in[0].gl_Position.xy;
    vec2 target = vert_target[0].xy;
    vec2 pos = in_position + time * (target - in_position);

    vec2 right = vec2(1.0, 0.0) * size;
    vec2 up = vec2(0.0, 1.0) * size;

    uv = vec2(1.0, 1.0);
    gl_Position = m_proj * vec4(pos + (right + up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(0.0, 1.0);
    gl_Position = m_proj * vec4(pos + (-right + up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(1.0, 0.0);
    gl_Position = m_proj * vec4(pos + (right - up), 0.0, 1.0);
    EmitVertex();

    uv = vec2(0.0, 0.0);
    gl_Position = m_proj * vec4(pos + (-right - up), 0.0, 1.0);
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