#This file is for parsing the motion data 
#from the json files and save them in fbx files

from FbxCommon import *
from pathlib import Path
from utils.skeleton import SkeletonAnimClip
from utils.fbx_utils import get_anim_layer, refresh_time_span
import argparse
import os
from tqdm import tqdm
import json

def json_to_fbx(source_file,target_file,use_fbx_model):
    with open(source_file, 'r') as h:
        motions = json.load(h)
    first_joint_name = motions["joint_name"][0]
    main_sdk_manager, main_scene = InitializeSdkObjects()
    lAxisSytemReference = main_scene.GetGlobalSettings().GetAxisSystem()
    src_f = Path(use_fbx_model)
    if not LoadScene(main_sdk_manager, main_scene, src_f.as_posix()):
        print(f'Load from {f.as_posix()} failed')
    main_anim_layer = get_anim_layer(main_scene,0,0)
    rootnode = main_scene.GetRootNode()
    cur_node = rootnode.FindChild(first_joint_name)
    assert cur_node
    anim_clip = SkeletonAnimClip()
    anim_clip.load_from_json(main_anim_layer, motions)
    anim_clip.export_to_fbx(main_anim_layer, cur_node)
    refresh_time_span(main_scene, main_scene.GetRootNode(),0,0,first_joint_name)
    SaveScene(main_sdk_manager, main_scene, target_file, 0)
    main_sdk_manager.Destroy()

def args_parsing(args):
    if(args.source_dir):
        if(not args.target_dir):
            print("missing target_dir, so return")
            return
        file_names = []
        for file in os.listdir(args.source_dir):
            if not file.endswith('.json'):
                continue
            file_names.append(file)
        if(len(file_names)==0):
            print("find no json files in source dir, so return")
            return
        Path(args.target_dir).mkdir(exist_ok=True, parents=True)
        pbar = tqdm(file_names)
        for file in pbar:
            pbar.set_description('Processing '+file)
            tmp_target = file[:-5] + ".fbx"
            tmp_target = os.path.join(args.target_dir,tmp_target)
            tmp_src = os.path.join(args.source_dir,file)
            json_to_fbx(tmp_src,tmp_target,args.use_fbx_model)
        print("finish parsing json and save to fbx!")
    elif(args.source_file):
        if(not args.target_file):
            print("missing target_file, so return")
            return
        if(not args.source_file.endswith('.json')):
            print("source_file is not json file, so return")
            return
        json_to_fbx(args.source_file,args.target_file,args.use_fbx_model)
    else:
        print("missing source_file or source_dir, so return")
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dir', type=str)
    parser.add_argument('--source_file', type=str)
    parser.add_argument('--target_dir', type=str)
    parser.add_argument('--target_file', type=str)
    parser.add_argument('--use_fbx_model', type=str,default="./fbx_model/motion_model.fbx")
    
    args = parser.parse_args()
    args_parsing(args)
