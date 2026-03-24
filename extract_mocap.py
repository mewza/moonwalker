from bvh import Bvh
import math

with open('moonwalk.bvh') as f:
    mocap = Bvh(f.read())

frames = mocap.nframes
fps    = 1.0 / mocap.frame_time
print(f"Frames: {frames}, FPS: {fps:.1f}")

def get_rot(frame, joint, channel):
    try:
        return mocap.frame_joint_channel(frame, joint, channel)
    except:
        return 0.0

def deg2rad(d):
    return d * math.pi / 180.0

def normalize(data, target_min, target_max):
    mn, mx = min(data), max(data)
    rng = mx - mn
    if rng < 0.0001:
        return [0.0] * len(data)
    return [round(target_min + (v - mn) / rng * (target_max - target_min), 4) for v in data]

def smooth_loop(data, blend=20):
    out = list(data)
    for i in range(blend):
        t = i / float(blend)
        out[-(blend - i)] = round(data[-(blend - i)] * (1.0 - t) + data[i] * t, 4)
    return out

hip_y_r   = []
spine_r   = []
l_thigh_r = []
r_thigh_r = []
l_knee_r  = []
r_knee_r  = []
l_arm_r   = []
r_arm_r   = []

for i in range(frames):
    hip_y_r.append(  deg2rad(get_rot(i, 'Hips',       'Yrotation')))
    spine_r.append(  deg2rad(get_rot(i, 'LowerBack',  'Xrotation')))
    l_thigh_r.append(deg2rad(get_rot(i, 'LeftUpLeg',  'Xrotation')))
    r_thigh_r.append(deg2rad(get_rot(i, 'RightUpLeg', 'Xrotation')))
    l_knee_r.append( deg2rad(get_rot(i, 'LeftLeg',    'Xrotation')))
    r_knee_r.append( deg2rad(get_rot(i, 'RightLeg',   'Xrotation')))
    l_arm_r.append(deg2rad(get_rot(i, 'LeftArm',  'Zrotation')))
    r_arm_r.append(deg2rad(get_rot(i, 'RightArm', 'Zrotation')))

hip_y   = smooth_loop(normalize(hip_y_r,   -0.30,  0.30))
l_thigh = smooth_loop(normalize(l_thigh_r, -0.8,  0.8))
r_thigh = smooth_loop(normalize(r_thigh_r, -0.8,  0.8))
l_knee  = smooth_loop(normalize([-x for x in l_knee_r],  0.0,  0.3))
r_knee  = smooth_loop(normalize([-x for x in r_knee_r],  0.0,  0.3))
l_arm = smooth_loop(normalize(l_arm_r, -0.8, 0.8))
r_arm = smooth_loop(normalize(r_arm_r, -0.8, 0.8))
spine   = smooth_loop(normalize(spine_r,   -0.05, 0.05))

def glsl_array(name, data):
    lines = [f"const float {name}[{len(data)}] = float[]("]
    for i in range(0, len(data), 10):
        chunk = data[i:i+10]
        suffix = ',' if i + 10 < len(data) else ''
        lines.append('    ' + ', '.join(str(v) for v in chunk) + suffix)
    lines.append(');')
    return '\n'.join(lines) + '\n'

out  = f"// Mocap — {frames} frames, playing @ 30fps\n"
out += f"#define MW_FRAMES {frames}\n"
out += f"#define MW_FPS    120.0\n\n"
out += glsl_array("mw_hip_y",  hip_y)
out += glsl_array("mw_spine",  spine)
out += glsl_array("mw_lthigh", l_thigh)
out += glsl_array("mw_rthigh", r_thigh)
out += glsl_array("mw_lknee",  l_knee)
out += glsl_array("mw_rknee",  r_knee)
out += glsl_array("mw_larm",   l_arm)
out += glsl_array("mw_rarm",   r_arm)

with open('moonwalk_glsl.txt', 'w') as f:
    f.write(out)

print(f"Done! {frames} frames written at 30fps playback")
