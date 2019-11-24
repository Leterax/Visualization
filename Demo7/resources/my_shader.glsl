#version 330

#if defined VERTEX_SHADER

in vec3 in_position;


void main() {
    gl_Position = vec4(in_position, 1.0);
}



    #elif defined FRAGMENT_SHADER
out vec4 fragColor;
in vec2 gl_FragCoord;
uniform float time;
uniform vec2 wnd_size;
uniform vec2 c;
uniform int iter;

uniform vec4 box;

void main() {
    vec2 z;
    vec2 uv = (gl_FragCoord.xy/wnd_size);

    z.x = box.x + uv.x * (box.z - box.x);
    z.y = box.y - uv.y * (box.y - box.w);

    int i;
    for (i=0; i<iter; i++) {
        float x = (z.x * z.x - z.y * z.y) + c.x;
        float y = (z.y * z.x + z.x * z.y) + c.y;

        if ((x * x + y * y) > 4.0) break;
        z.x = x;
        z.y = y;
    }

    fragColor = vec4((i == iter ? 0.0 : float(i)) / 100.0);
}
    #endif

