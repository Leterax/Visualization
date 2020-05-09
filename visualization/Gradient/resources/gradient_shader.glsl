#version 330

#if defined VERTEX_SHADER

in vec3 in_position;


void main() {
    gl_Position = vec4(in_position, 1.0);
}



#elif defined FRAGMENT_SHADER
out vec4 fragColor;
uniform float speed;
uniform float time;
uniform vec2 wnd_size;
void main() {

    vec3 color1 = vec3((sin(time*speed) + 1.0) / 2., (sin((time + 2.)*speed) + 1.0) / 2., (sin((time + 3.)*speed) + 1.0) / 2.);
    vec3 color2 = vec3(1.)-color1;
    float dst = length(vec2(.5, .5)-gl_FragCoord.xy/wnd_size);
    vec3 color = (color2-color1) * dst + color1;
    fragColor = vec4(color, 1.);


}

    #endif

