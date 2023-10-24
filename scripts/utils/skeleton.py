from collections import deque
from copy import deepcopy

import numpy as np
from FbxCommon import *
from utils.fbx_utils import fbx_vector3_to_np, get_quaternion, get_translation,get_amatrix_np
from utils.quaternion import (euler_to_quaternion, qeuler_np, qinv_np, qmul_np,
                        qrot_np,qfix)
import json

def get_node_name(nodequeue):
    node_name = deque([])
    for cur_node in nodequeue:
        node_name.append(cur_node.GetName())
    return node_name


class SkeletonAnimClip:

    FPS = 30

    def __init__(self):
        self.joint_quaternion = None
        self.joint_name = None
        self.joint_parent = None
        self.joint_lcl_translation = None
        self.joint_position = None
        self.joint_PreRotation = None
        self.joint_PreRotationOffset = None
        self.joints_type = 0

    def set_joints_type(self,joints_type):
        self.joints_type = joints_type

    def save_to_json(self,target_file):
        with open(target_file, 'w') as h:
            json.dump({
                'joint_name': self.joint_name,
                'root_translation': self.root_translation.tolist(),
                'joints_type':self.joints_type,
                'joint_quaternion':self.joint_quaternion.tolist()
            }, h)

    def load_from_fbx(self, anim_layer, root_node):
        t_curve = root_node.LclTranslation.GetCurve(anim_layer, 'X')
        num_keys = t_curve.KeyGetCount()
        root_translation = []
        for i in range(num_keys):
            root_tran = np.zeros(3)
            for c_ind, c in enumerate(['X','Y','Z']):
                t_curve = root_node.LclTranslation.GetCurve(anim_layer, c)
                root_tran[c_ind] = t_curve.KeyGetValue(i)
            root_translation.append(root_tran)
        self.root_translation = np.array(root_translation)
        self.root_translation -= np.mean(self.root_translation,axis=0)
        self.joint_quaternion = []
        self.joint_PreRotation = []
        self.joint_PreRotationOffset = []
        node_queue = deque([root_node])
        self.joint_name = [root_node.GetName()]
        self.joint_parent = [-1]
        self.joint_lcl_translation = [fbx_vector3_to_np(root_node.LclTranslation.Get())]
        processed_node_cnt = 0

        while len(node_queue) > 0:
            cur_node = node_queue.popleft()
            cur_time = t_curve.KeyGetTime(0)
            for i in range(cur_node.GetChildCount()):
                cur_child = cur_node.GetChild(i)
                node_queue.append(cur_child)
                self.joint_name.append(cur_child.GetName())
                self.joint_parent.append(processed_node_cnt)
                self.joint_lcl_translation.append(fbx_vector3_to_np(cur_child.LclTranslation.Get()))
            cur_quaters = []
            r_curves = [cur_node.LclRotation.GetCurve(anim_layer, c) for c in ['X', 'Y', 'Z']]
            for i in range(num_keys):
                rRotation = np.zeros(3)
                if(r_curves[0]):
                    for j in range(3):
                        rRotation[j] = r_curves[j].KeyGetValue(i)
                cur_quaters.append(euler_to_quaternion(rRotation*np.pi/180,'zyx'))
            self.joint_quaternion.append(np.array(cur_quaters))
            processed_node_cnt += 1
        self.joint_lcl_translation = np.array(self.joint_lcl_translation)
        self.joint_quaternion = np.array(self.joint_quaternion)
        
    def load_from_json(self, anim_layer, json_motion):
        self.root_translation = np.array(json_motion["root_translation"])
        self.joint_name = json_motion["joint_name"]
        self.joint_quaternion = np.array(json_motion["joint_quaternion"])
        self.joints_type = json_motion["joints_type"]

    def move_root(self, target_t, target_q):
        q0 = self.joint_quaternion[0, 0]
        num_frames = self.joint_quaternion.shape[1]
        dq = qmul_np(target_q, qinv_np(q0))
        dq = np.tile(dq, [num_frames, 1])
        self.joint_quaternion[0] = qmul_np(dq, self.joint_quaternion[0])

        self.root_translation = self.root_translation - self.root_translation[[0]]
        self.root_translation = qrot_np(dq, self.root_translation)
        self.root_translation = self.root_translation + target_t[np.newaxis, :]

    def reset_root(self):
        q0 = self.joint_quaternion[0, 0]
        euler0 = qeuler_np(q0, 'yxz')
        euler0[1] = 0
        target_q = euler_to_quaternion(euler0, 'yxz')

        target_t = self.root_translation[0]
        target_t = np.array([0, target_t[1], 0])
        self.move_root(target_t, target_q)
        
    def print_skeleton_from_fbx(self, anim_layer, root_node):
        node_queue = deque([root_node])
        while len(node_queue) > 0:
            print(get_node_name(node_queue))
            child_node_queue = deque([])
            for cur_node in node_queue:
                for i in range(cur_node.GetChildCount()):
                    child_node_queue.append(cur_node.GetChild(i))
            node_queue = child_node_queue

    def print_quaternion(self, anim_layer, root_node,frame_num):
        node_queue = deque([root_node])
        while len(node_queue) > 0:
            child_node_queue = deque([])
            for cur_node in node_queue:
                cur_quarternion = get_quaternion(anim_layer, cur_node, frame_num)
                for i in range(cur_node.GetChildCount()):
                    child_node_queue.append(cur_node.GetChild(i))
            node_queue = child_node_queue    

    def export_to_fbx(self, anim_layer, root_node):
        dt = FbxTime()
        dt.SetSecondDouble(1/self.FPS)

        for c_ind, c in enumerate(['X','Y','Z']):
            t_curve = root_node.LclTranslation.GetCurve(anim_layer, c)
            num_keys = t_curve.KeyGetCount()
            t_curve.KeyModifyBegin()
            t_curve.KeyRemove(0, num_keys - 1)
            for i in range(self.root_translation.shape[0]):
                key_index = t_curve.KeyAdd(dt*i)[0]
                t_curve.KeySetValue(key_index, self.root_translation[i, c_ind])
            t_curve.KeyModifyEnd()
        for node_ind, node_name in enumerate(self.joint_name):
            cur_node = root_node.FindChild(node_name)
            if(node_name == root_node.GetName()):
                cur_node = root_node
            if(not cur_node):
                continue
            node_quater = self.joint_quaternion[node_ind]
            # print(type(node_quater))
            if(type(node_quater).__name__=='list'):
                node_quater = np.array(node_quater,dtype='float64')
            node_rotation = qeuler_np(node_quater, 'zyx')* 180 / np.pi
            assert cur_node
            r_curves = [cur_node.LclRotation.GetCurve(anim_layer, c) for c in ['X', 'Y', 'Z']]
            if(not r_curves[0]):
                continue
            num_keys = r_curves[0].KeyGetCount()
            for curve in r_curves:
                curve.KeyModifyBegin()
                curve.KeyRemove(0, num_keys - 1)
            for i in range(self.joint_quaternion.shape[1]):
                for j in range(3):
                    key_index = r_curves[j].KeyAdd(dt*i)[0]
                    r_curves[j].KeySetValue(i, node_rotation[i, j])
            for curve in r_curves:
                curve.KeyModifyEnd()
