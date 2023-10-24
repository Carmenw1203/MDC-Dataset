import pandas as pd
from pathlib import Path
import json
import os
import numpy as np

__all__ = ['Lang']


class Lang:
    SOD = 0
    EOD = 1

    def __init__(self, name):
        self.name = name
        self.movement2index = {}
        self.movement2beat_num = {}
        self.movement2beat_frame = {}
        self.movement2root_trans = {}
        self.movement2joint_quaternion = {}
        self.index2movement = {}
        self.n_movements = 0
        self.joint_name = None
        self.joint_num = None
        self.joint_type = None
        self.max_start_len = 0 
        self.add_special_move()

    def add_special_move(self):
        self.add_movements('SOD',1)
        self.add_movements('EOD',1)
        self.add_movements('NIL',1)

    def add_movements(self,movement_tag,beat_num):
        self.movement2index[movement_tag] = self.n_movements
        self.index2movement[self.n_movements] = movement_tag
        self.movement2beat_num[movement_tag] = beat_num
        self.n_movements += 1

    def index2beat_num(self, ind):
        return self.movement2beat_num[self.index2movement[ind]]

    def load_from_csv(self,mu_csv,motion_json_dir):
        mu_file = pd.read_csv(mu_csv)
        for ind, row in mu_file.iterrows():
            movement_tag = row['Movement_tag']
            source_file = os.path.join(motion_json_dir,row['Source_file'])
            assert source_file.endswith('.fbx')
            source_file = source_file[:-4] + '.json'
            beat_num = row['Beats']
            start_frame = row["Start_frame"]
            end_frame = row["End_frame"]
            beat_frame = []
            if("Start" in movement_tag.split("-")):
                for i in range(beat_num):
                    beat_frame.append(row[5+i]- start_frame)
                if(self.max_start_len < beat_num):
                    self.max_start_len = beat_num
            else:
                for i in range(beat_num):
                    beat_frame.append(row[5+i]- start_frame)
            self.movement2beat_frame[movement_tag] = beat_frame
            self.movement2beat_num[movement_tag] = beat_num
            self.index2movement[self.n_movements] = movement_tag
            self.movement2index[movement_tag] = self.n_movements
            with open(source_file, 'r') as h:
                motions = json.load(h)
            if(self.joint_type == None):
                self.joint_type = motions['joints_type']
                self.joint_name = motions['joint_name']
                self.joint_num = len(self.joint_name)
            self.movement2root_trans[movement_tag] = np.array(motions['root_translation'], dtype='float64')[start_frame:int(end_frame+1)]
            self.movement2joint_quaternion[movement_tag] = np.array(motions['joint_quaternion'], dtype='float64')[:,start_frame:int(end_frame+1)]
            self.n_movements += 1

