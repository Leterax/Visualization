#version 330

#if defined VERTEX_SHADER

in vec3 in_position;

void main() {
    gl_Position = vec4(in_position, 1.0);

}

    #elif defined FRAGMENT_SHADER

in vec2 gl_FragCoord;
out vec4 fragColor;

float rand(vec2 co){
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

void main() {
    fragColor = vec4(1., 0., 0., rand(gl_FragCoord) > .5 ? 0. : 1.);

}
    #endif