#version 430

#if defined VERTEX_SHADER
in vec3 in_position;
in vec3 ball_position;
in vec3 ball_velocity;
in vec4 ball_color;

uniform mat4 m_projection;
uniform mat4 m_camera;

out vec4 color;
out vec3 vel;

void main(){
    color = ball_color;
    vel = ball_velocity;
    gl_Position = m_projection * m_camera * vec4(in_position + ball_position, 1.);
}


#elif defined FRAGMENT_SHADER

out vec4 fragColor;
in vec4 color;
in vec3 vel;

void main() {

    float _ = length(vel);
    fragColor = color * _ / _;
}
#endif
