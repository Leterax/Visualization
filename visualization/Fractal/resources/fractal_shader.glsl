#version 400

#if defined VERTEX_SHADER

in vec3 in_position;


void main() {
    gl_Position = vec4(in_position, 1.0);
}

#elif defined FRAGMENT_SHADER
out vec4 fragColor;
layout(pixel_center_integer) in vec4 gl_FragCoord;

uniform float time;
uniform vec2 wnd_size;

uniform vec2 c;
uniform int iter;
uniform float R;

uniform vec2 center;
uniform float zoom;


vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    dvec2 uv = (((gl_FragCoord.xy/wnd_size-.5)*2)*zoom)+center;

    double zx = uv.x * R;
    double zy = uv.y * R;

    int i = 0;
    while ((zx*zx+zy*zy < R*R) && (i < iter)){
        double xtemp = zx * zx - zy * zy;
        zy = 2 * zx * zy + c.y;
        zx = xtemp + c.x;
        i = i+1;
    }
    vec3 color = hsv2rgb(vec3(float(i)/iter, .5, .7));
    if (i==iter){
        fragColor = vec4(0.);
    }
    else {
        fragColor = vec4(color, 1.);
    }

}
#endif

