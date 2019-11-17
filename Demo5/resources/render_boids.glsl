#version 330

#if defined VERTEX_SHADER

in vec2 in_position;
void main() {
    gl_Position = vec4(in_position, 0., 1.);
}

    #elif defined FRAGMENT_SHADER

out vec4 fragColor;

void main() {
    fragColor = vec4(1., 0., 0., 1.);
}


    #endif

