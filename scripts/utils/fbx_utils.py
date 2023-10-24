import numpy as np
from FbxCommon import *

def get_amatrix_np(amatrix):
    len_am = 4
    amatrix_np = np.zeros([4,4])
    for i in range(len_am):
        for j in range(len_am):
            amatrix_np[j,i] = amatrix.Get(i,j)
    return amatrix_np

def get_amatrix(anim_layer, node, key_index):
    r_curve = node.LclRotation.GetCurve(anim_layer, 'X')
    if not r_curve:
        return None
    num_keys = r_curve.KeyGetCount()
    key_index = (key_index + num_keys) % num_keys
    cur_time = r_curve.KeyGetTime(key_index)
    amatrix = node.EvaluateLocalTransform(cur_time, 0, False, True)
    return amatrix


def get_quaternion(anim_layer, node, key_index):
    amatrix = get_amatrix(anim_layer, node, key_index)
    if not amatrix:
        return np.array([0, 0, 0, 0])
    q = amatrix.GetQ()
    q = np.array([q[3], q[0], q[1], q[2]])
    return q


def get_translation(anim_layer, node, key_index):
    t_curve = node.LclTranslation.GetCurve(anim_layer, 'X')
    if not t_curve:
        return None
    num_keys = t_curve.KeyGetCount()
    key_index = (key_index + num_keys) % num_keys
    cur_time = t_curve.KeyGetTime(key_index)
    trans = node.EvaluateLocalTranslation(cur_time, 0, False, True)
    trans = np.array([trans[0], trans[1], trans[2]])
    return trans


def fbx_vector3_to_np(v):
    return np.array([v[0], v[1], v[2]])


def get_anim_layer(scene,stack_id,layer_id):
    anim_stack = scene.GetSrcObject(FbxCriteria.ObjectType(FbxAnimStack.ClassId), stack_id)
    if not anim_stack:
        print('No animation stack in the fbx file')
        sys.exit(1)
    anim_layer = anim_stack.GetSrcObject(FbxCriteria.ObjectType(FbxAnimLayer.ClassId), layer_id)
    if not anim_layer:
        print('No animation layer')
        sys.exit(1)

    return anim_layer

def refresh_time_span(scene, root_node,stack_id,layer_id,root_name):
    anim_stack = scene.GetSrcObject(FbxCriteria.ObjectType(FbxAnimStack.ClassId), stack_id)
    time_span = anim_stack.GetLocalTimeSpan()
    anim_layer = anim_stack.GetSrcObject(FbxCriteria.ObjectType(FbxAnimLayer.ClassId), layer_id)
    root_node = root_node.FindChild(root_name)
    r_curve = root_node.LclRotation.GetCurve(anim_layer, 'X')
    num_keys = r_curve.KeyGetCount()
    first_time = r_curve.KeyGetTime(0)
    last_time = r_curve.KeyGetTime(num_keys - 1)
    time_span.SetStart(first_time)
    time_span.SetStop(last_time)
    anim_stack.SetLocalTimeSpan(time_span)