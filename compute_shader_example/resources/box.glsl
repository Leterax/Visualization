#version 430

#if defined VERTEX_SHADER
in vec3 in_position;

uniform mat4 m_projection;
uniform mat4 m_camera;

void main(){
    gl_Position = m_projection * m_camera * vec4(in_position, 1.);

}

    #elif defined FRAGMENT_SHADER

out vec4 fragColor;

void main(){

    fragColor = vec4(0, 1, 0, .25);
}
    #endif
