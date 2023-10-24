import sys
import numpy as np
import random
from utils.lang import Lang
from utils.quaternion import qeuler_np
from scipy.spatial.transform import Slerp
from scipy.spatial.transform import Rotation as R
import math
__all__ = ['MovementGlue']
sys.path.append("..")

def check_acute(v0, v1):
    dot_products = np.sum(v0*v1,axis=1)
    mask = dot_products < 0
    return mask
def slerp(v0, v1, t):
    DOT_THRESHOLD = 0.9995
    t = np.expand_dims(t,-1).repeat(4,axis=-1)
    v0 = v0 / np.linalg.norm(v0)
    v1 = v1 / np.linalg.norm(v1)
    dot = v0.dot(v1)
    
    if dot < 0:
        v0 = v0*-1
        dot = v0.dot(v1)
    
    if np.abs(dot) > DOT_THRESHOLD:
        v2 = (1 - t) * v0 + t * v1
    else:
        theta_0 = np.arccos(dot)
        sin_theta_0 = np.sin(theta_0)
        theta_t = theta_0 * t
        sin_theta_t = np.sin(theta_t)
        s0 = np.sin(theta_0 - theta_t) / sin_theta_0
        s1 = sin_theta_t / sin_theta_0
        v2 = s0 * v0 + s1 * v1
    return v2

def lerp(v0, v1, t):#linear interpolation
    
    result = t[:, np.newaxis] * (v1 - v0)[np.newaxis, :] + v0[np.newaxis, :]
    return result

class MovementGlue:
    ORI_FPS = 30.0

    def __init__(self, lang, args):
        self.lang = lang
        self.linear_interpolation_len = args.linear_interpolation_len
        self.joint_num = lang.joint_num

    def add_start_tag(self,movement_tags,beats, start_time, cur_dancer):
        # add start tags to the movement_tags
        # first calculate the number of beats before the main part
        nil_cnt = 0
        for bt in beats:
            if bt < start_time:
                nil_cnt += 1
        start_beats_num = nil_cnt

        pos_cnt = 0
        while(start_beats_num > 0):
            max_start_len = self.lang.max_start_len
            if(start_beats_num > max_start_len):
                start_beats_num -= max_start_len
                movement_tags.insert(pos_cnt,cur_dancer+"-Start-{}".format(max_start_len))
            else:
                movement_tags.insert(pos_cnt,cur_dancer+"-Start-{}".format(start_beats_num))
                start_beats_num = 0
            pos_cnt += 1 
        new_tags = []
        for item in movement_tags:
            if(item == 'NIL'):
                continue
            else:
                new_tags.append(item)
        return new_tags

    def glue(self,movement_tags,beats=[],music_len=0):
        root_translation = np.empty(shape = (0,3))
        joint_quaternion = np.empty(shape = (self.joint_num,0,4))
        beat_frames = np.empty(shape = (0))

        # linear interpoaltion
        t = np.array(range(1, self.linear_interpolation_len + 1)) / (self.linear_interpolation_len + 1)
        beat_frames = np.concatenate((beat_frames,np.array(self.lang.movement2beat_frame[movement_tags[0]])+root_translation.shape[0]),axis=0)
        root_translation = self.lang.movement2root_trans[movement_tags[0]]
        joint_quaternion = self.lang.movement2joint_quaternion[movement_tags[0]]
        cur_frame = 0
        gap_start_frame = []
        gap_end_frame = []
        smooth_times = 0
        smooth_t_list = []
        # warping the movements
        for i in range(1,len(movement_tags)):
            cur_frame = root_translation.shape[0]
            gap_start_frame.append(cur_frame)
            gap_end_frame.append(cur_frame + self.linear_interpolation_len)
            smooth_times += 1
            smooth_t_list.append(t)
            root_trans_zero = np.zeros(shape = (self.linear_interpolation_len,3))
            joint_quater_zero = np.zeros(shape = (self.joint_num,self.linear_interpolation_len,4))
            beat_frames = np.concatenate((beat_frames,np.array(self.lang.movement2beat_frame[movement_tags[i]])+root_translation.shape[0]+self.linear_interpolation_len),axis=0)
            
            next_frame = self.lang.movement2joint_quaternion[movement_tags[i]][:,0]
            last_frame = joint_quaternion[:,0]
            mask = check_acute(last_frame,next_frame)
            next_motion = self.lang.movement2joint_quaternion[movement_tags[i]].copy()
            for k in range(mask.shape[0]):
                if(mask[k]):
                    next_motion[k] *= -1
            joint_quaternion = np.concatenate((joint_quaternion,joint_quater_zero,next_motion),axis=1)
            root_translation = np.concatenate((root_translation,root_trans_zero,self.lang.movement2root_trans[movement_tags[i]]),axis=0)
        for j in range(smooth_times):
            last_root_trans = root_translation[gap_start_frame[j] - 1]
            next_root_trans = root_translation[gap_end_frame[j]]
            root_inter = lerp(last_root_trans,next_root_trans,smooth_t_list[j])
            root_translation[gap_start_frame[j] : gap_end_frame[j]] = root_inter
            last_joint_quater = joint_quaternion[:,gap_start_frame[j] - 1]
            next_joint_quater = joint_quaternion[:,gap_end_frame[j]]
            quater_inter = []

            for k in range(last_joint_quater.shape[0]):
                quater_inter.append(slerp(last_joint_quater[k],next_joint_quater[k],smooth_t_list[j]))
            quater_inter = np.array(quater_inter)
            joint_quaternion[:,gap_start_frame[j] : gap_end_frame[j]] = quater_inter
        # fixed the root trans in horizontal plane
        root_translation[:,0] = 0
        root_translation[:,2] = 0

        root_translation,joint_quaternion = self.align_to_music(music_len,beat_frames.astype(int),beats,root_translation,joint_quaternion)

        return root_translation, joint_quaternion
    
    def align_to_music(self,music_len,beat_frames,beats,root_translation,joint_quaternion):
        target_frame_num = int(self.ORI_FPS*music_len) + 1
        aligned_root_trans = np.zeros(shape = (target_frame_num,3), dtype='float64')
        aligned_joint_quater = np.zeros(shape = (self.joint_num,target_frame_num,4), dtype='float64')
        cur_frame = beat_frames[0]
        cur_target_frame = int(self.ORI_FPS*beats[0])
        if cur_target_frame == 0:
            cur_target_frame = 1
        aligned_root_trans[cur_target_frame] = root_translation[cur_frame]
        aligned_joint_quater[:,cur_target_frame] = joint_quaternion[:,cur_frame]
        
        for j in range(cur_target_frame):
            aligned_root_trans[j] = root_translation[int(float(j)*float(cur_frame)/float(cur_target_frame))]
            aligned_joint_quater[:,j] = joint_quaternion[:,int(float(j)*float(cur_frame)/float(cur_target_frame))]
        
        for i in range(1,beat_frames.shape[0]):
            pre_frame = beat_frames[i-1]
            pre_target_frame = int(self.ORI_FPS*beats[i-1])
            if pre_target_frame == 0:
                pre_target_frame = 1
            cur_frame = beat_frames[i]
            cur_target_frame = int(self.ORI_FPS*beats[i])
            aligned_root_trans[cur_target_frame] = root_translation[cur_frame]
            aligned_joint_quater[:,cur_target_frame] = joint_quaternion[:,cur_frame]
            sample_rate =float(cur_frame - pre_frame)/float(cur_target_frame - pre_target_frame)
            for j in range(pre_target_frame,cur_target_frame):
                aligned_root_trans[j] = root_translation[int(float(j-pre_target_frame)*sample_rate)+pre_frame]
                aligned_joint_quater[:,j] = joint_quaternion[:,int(float(j-pre_target_frame)*sample_rate)+pre_frame]
        for k in range(beat_frames[-1],root_translation.shape[0]):
            if(int(float(k-beat_frames[-1])/sample_rate)+cur_target_frame >= target_frame_num):
                break
            aligned_root_trans[int(float(k-beat_frames[-1])/sample_rate)+cur_target_frame] = root_translation[k]
            aligned_joint_quater[:,int(float(k-beat_frames[-1])/sample_rate)+cur_target_frame] = joint_quaternion[:,k]

        freeze_frame = int(float(root_translation.shape[0]-1-beat_frames[-1])/sample_rate)+cur_target_frame
        for j in range(freeze_frame+1,target_frame_num):
            aligned_root_trans[j] = aligned_root_trans[freeze_frame]
            aligned_joint_quater[:,j] = aligned_joint_quater[:,freeze_frame]
        return aligned_root_trans,aligned_joint_quater
