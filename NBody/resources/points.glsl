#version 430

#if defined VERTEX_SHADER
in vec4 in_position;
in vec4 in_color;

out vec4 color;


uniform mat4 m_projection;
uniform mat4 m_camera;

void main(){
    gl_Position = m_projection * m_camera * vec4(in_position.xyz, 1.);

    color = vec4(in_color);



}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;
in vec4 color;

void main(){
    fragColor = color;
}
#endif
