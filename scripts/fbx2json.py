#This file is for parsing the motion data 
#from the fbx files and save them in json files
from FbxCommon import *
from pathlib import Path
from utils.skeleton import SkeletonAnimClip
from utils.fbx_utils import get_anim_layer, refresh_time_span
from collections import deque
import argparse
import os
from tqdm import tqdm


def fbx_to_json(source_file,target_file,hip_node_name):
    print(source_file)
    main_sdk_manager, main_scene = InitializeSdkObjects()
    lAxisSytemReference = main_scene.GetGlobalSettings().GetAxisSystem()
    src_f = Path(source_file)
    if not LoadScene(main_sdk_manager, main_scene, src_f.as_posix()):
        print(f'Load from {f.as_posix()} failed')

    rootnode = main_scene.GetRootNode()
    cur_node = rootnode.FindChild(hip_node_name)
    # print(rootnode.GetName())
    assert cur_node
    main_anim_layer = get_anim_layer(main_scene,0,0)
    
    anim_clip = SkeletonAnimClip()
    anim_clip.load_from_fbx(main_anim_layer, cur_node)
    anim_clip.save_to_json(target_file)
    main_sdk_manager.Destroy()


def args_parsing(args):
    if(args.source_dir):
        if(not args.target_dir):
            print("missing target_dir, so return")
            return
        file_names = []
        for file in os.listdir(args.source_dir):
            if not file.endswith('.fbx'):
                continue
            file_names.append(file)
        if(len(file_names)==0):
            print("find no fbx files in source dir, so return")
            return
        Path(args.target_dir).mkdir(exist_ok=True, parents=True)
        pbar = tqdm(file_names)
        for file in pbar:
            pbar.set_description('Processing '+file)
            tmp_target = file[:-4] + ".json"
            tmp_target = os.path.join(args.target_dir,tmp_target)
            tmp_src = os.path.join(args.source_dir,file)
            fbx_to_json(tmp_src,tmp_target,args.hip_node_name)
        print("finish parsing fbx and save to json!")
    elif(args.source_file):
        if(not args.target_file):
            print("missing target_file, so return")
            return
        if(not args.source_file.endswith('.fbx')):
            print("source_file is not fbx file, so return")
            return
        fbx_to_json(args.source_file,args.target_file,args.hip_node_name)
    else:
        print("missing source_file or source_dir, so return")
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dir', type=str)
    parser.add_argument('--source_file', type=str)
    parser.add_argument('--target_dir', type=str)
    parser.add_argument('--target_file', type=str)
    parser.add_argument('--hip_node_name', type=str,default="Biped_Root")
    
    args = parser.parse_args()
    args_parsing(args)


