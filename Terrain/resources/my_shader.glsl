#version 400

#if defined VERTEX_SHADER

in vec3 in_position;

uniform mat4 projection;

void main() {
    gl_Position = (projection * vec4(in_position, 1.0));
}

    #elif defined FRAGMENT_SHADER

out vec4 fragColor;
void main() {

    fragColor = vec4(0., 1., 0., 1);

}

    #endif

