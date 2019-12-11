#version 330

#if defined VERTEX_SHADER

in vec3 in_position;


void main() {
    gl_Position = vec4(in_position, 1.0);
}



    #elif defined FRAGMENT_SHADER

out vec4 fragColor;
in vec2 gl_FragCoord;
uniform vec2 wnd_size;
uniform float speed;
uniform float time;

vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = (gl_FragCoord.xy/wnd_size - vec2(.5)) * 2.;
    float dst = length(uv);

    if (dst > .4 && dst < .7){
        vec3 color = hsv2rgb(vec3(mod((atan(uv.y, uv.x)/(3.14159265359*2)+time*speed)+1., 2.)-1., dst*2., 1));
        fragColor = vec4(color, 1.);
    }
    else {
        fragColor = vec4(0., 0., 0., 1.);
    }


}

    #endif

