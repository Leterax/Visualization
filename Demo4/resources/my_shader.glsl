#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
in vec2 in_texcoord_0;

uniform mat4 m_camera;
uniform mat4 model;
uniform mat4 projection;

out vec2 uv;
void main() {
    gl_Position = (projection * m_camera * model * vec4(in_position, 1.0));
    uv = in_texcoord_0;
}



    #elif defined FRAGMENT_SHADER

out vec4 fragColor;
in vec2 uv;
void main() {

//    vec2 pos = (uv - vec2(0.5)) * vec2(2.0);
//    float border = step(0.9, abs(pos.x)) + step(0.9, abs(pos.y));
//    fragColor = vec4(vec3(border), 1.0);

    if ((uv.x < 0.01 || uv.x > 0.99) || (uv.y < 0.01 || uv.y > 0.99)){

        fragColor = vec4(0.15686275, 0.07843137, 0.56078431, 1);
    }
    else{
        fragColor = vec4(0.08627451, 0.56862745, 0.10980392, 1);
    }

}

    #endif

