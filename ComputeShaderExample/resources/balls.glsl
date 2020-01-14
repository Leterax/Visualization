#version 430

#if defined VERTEX_SHADER
in vec3 in_position;
in vec4 ball_position;

uniform mat4 m_projection;
uniform mat4 m_camera;

void main(){
    gl_Position = m_projection * m_camera * vec4(in_position + ball_position.xyz, 1.);
}
#endif
