#This file is written for stitching the dance-movements(
import os
import json
from utils.lang import Lang
from utils.time_process import time_str2sec,time_str2sec_list
from utils.acoustics import Acoustics
import argparse
from pathlib import Path
from utils.glue_movements import MovementGlue

def Visualize_Ground_Truth(args,glue,acoustics):
    print("original demo")
    Path(args.target_dir).mkdir(exist_ok=True, parents=True) 
    with open(args.choreo_raw, 'r') as h:
        dances = json.load(h)

    for dance in dances:
        file_index = dance["Filename"][:-4]
        movement_start_time = time_str2sec(dance["Start_time"])
        movement_tags = dance["Movements"]
        movement_end_times = time_str2sec_list(dance["Movements_end_time"])
            
        movement_tags = glue.add_start_tag(movement_tags,acoustics.index2beats[file_index],movement_start_time,args.cur_dancer)
        motion_root_trans, motion_joint_quater = glue.glue(movement_tags,acoustics.index2beats[file_index],acoustics.index2music_len[file_index]) # motion align to music

        #save the movements to json
        output_filename = os.path.join(args.target_dir,dance["Filename"][:-4] +".json")
        with open(output_filename, 'w') as h:
            json.dump({
                'joint_name': lang.joint_name,
                'root_translation': motion_root_trans.tolist(),
                'joints_type': lang.joint_type,
                'joint_quaternion': motion_joint_quater.tolist()
            }, h)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--choreo_raw', type=str,default=None,help="set the choreo raw data file")
    parser.add_argument('--choreo_inference', type=str,default=None,help="set the choreo inference data file when cau_source == generate_inference")
    parser.add_argument('--acoustic_raw', type=str,default="./data/acoustic_feature/")
    parser.add_argument('--motion_json_dir', type=str,default="./data/motion_json/")
    parser.add_argument('--mu_csv', type=str,default="./data/cau_csv/kieren/hiphop_cau.csv")
    parser.add_argument('--target_file', type=str,default="../output_jsons/test_stitch_short.json")
    parser.add_argument('--target_dir', type=str,default='./output/original_demo/')
    parser.add_argument('--joint_json', type=str,default="./data/joint_json/hiphop_correct.json")
    parser.add_argument("--linear_interpolation_len",type=int,default=4)
    parser.add_argument("--cur_dancer",type=str)
    parser.add_argument("--chs_post_processing",type=int,default=0)

    args = parser.parse_args()
    lang = Lang(args.cur_dancer)
    lang.load_from_csv(args.mu_csv,args.motion_json_dir)
    glue = MovementGlue(lang,args)
    acoustics = Acoustics(args.acoustic_raw)

    Visualize_Ground_Truth(args,glue,acoustics)
