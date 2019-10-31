#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 target;

uniform float time;
uniform mat4 m_proj;

void main() {
    vec2 interp = in_position + time * (target-in_position);
    gl_Position = m_proj * vec4(interp, 0.0, 1.0);
}

#elif defined GEOMETRY_SHADER

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

void main() {
    const float size = 0.01;

    vec2 pos = gl_in[0].gl_Position.xy;
    vec2 right = vec2(1.0, 0.0) * size;
    vec2 up = vec2(0.0, 1.0) * size;

    gl_Position = vec4(pos + (right + up), 0.0, 1.0);
    EmitVertex();

    gl_Position = vec4(pos + (-right + up), 0.0, 1.0);
    EmitVertex();

    gl_Position = vec4(pos + (right - up), 0.0, 1.0);
    EmitVertex();

    gl_Position = vec4(pos + (-right - up), 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;

void main() {
    fragColor = vec4(1.0);
}
#endif