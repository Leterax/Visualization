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

#elif defined FRAGMENT_SHADER

out vec4 fragColor;

void main() {
    fragColor = vec4(1.0);
}
#endif