import os
import pathlib
import json
import numpy as np


__all__ = ['Acoustics']

class Acoustics:
    def __init__(self, acoustic_raw, beat_fps=100, chroma_fps=10):
        acoustic_feature_dir = acoustic_raw
        self.index2beats = {}
        self.index2chroma = {}
        self.index2beat_act = {}
        self.index2onsets = {}
        self.index2music_len = {}
        for file in os.listdir(acoustic_feature_dir):
            if not file.endswith('.json'):
                continue
            file_index = file[:-5]
            file_path =  os.path.join(acoustic_feature_dir,file)
            with open(file_path, 'r') as h:
                acoustics_feature = json.load(h)
            self.index2beat_act[file_index] = np.array(acoustics_feature["beat_act"])
            self.index2music_len[file_index] = self.index2beat_act[file_index].shape[0]/beat_fps
            self.index2beats[file_index] = np.array(acoustics_feature["beats"])
            self.index2onsets[file_index] = np.array(acoustics_feature["onsets"])
            self.index2chroma[file_index] = np.array(acoustics_feature["chroma"])
        self.beat_fps = beat_fps
        self.chroma_fps = chroma_fps
    
    def get_beat_num(self, music_id):
        beats = self.index2beats[music_id]
        return beats.shape[0]

