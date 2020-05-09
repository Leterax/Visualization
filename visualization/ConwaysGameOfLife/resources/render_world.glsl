#version 330
#if defined VERTEX_SHADER

in vec3 in_position;
in vec2 in_texcoord_0;

out vec2 uv;

void main() {
    gl_Position = vec4(in_position, 1.0);
    uv = in_texcoord_0;
}

    #elif defined FRAGMENT_SHADER
in vec2 uv;

uniform sampler2D texture0;

uniform float scale;
uniform vec2 scaleCenter;

out vec4 fragColor;

void main() {
    vec2 gv = (uv-vec2(.5))*2.;
    gv = gv * scale;
    gv = gv + scaleCenter;

    if (gv.x < 0. || gv.y < 0. || gv.x > 1. || gv.y > 1.){
        fragColor = vec4(0, 0, 0, 0);
    } else {
        fragColor = vec4(texture(texture0, gv));
    }

}
    #endif