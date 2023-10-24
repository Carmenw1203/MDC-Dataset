import os
import json
import pathlib
import numpy as np
import argparse
from tqdm import tqdm
from madmom.features.beats import RNNBeatProcessor, BeatTrackingProcessor
from madmom.features.onsets import CNNOnsetProcessor
from madmom.audio.chroma import DeepChromaProcessor


def extract_acoustic_feature(args):
    cur_music_dir = os.path.join(args.music_dir, args.music_type)
    save_dir = os.path.join(args.acoustic_feature_dir, args.music_type)
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
    for file in tqdm(os.listdir(cur_music_dir)):
        if not file.endswith('.wav'):
            continue
        cur_music_path = os.path.join(cur_music_dir,file)
        save_path = os.path.join(save_dir,file[:-4]+".json")
        act = RNNBeatProcessor()(cur_music_path)
        beats = BeatTrackingProcessor(fps=100)(act)
        onsets = CNNOnsetProcessor()(cur_music_path)
        chroma = DeepChromaProcessor()(cur_music_path)
        with open(save_path, 'w') as h:
            json.dump({
                'beat_act':act.tolist(),
                'beats':beats.tolist(),
                'onsets':onsets.tolist(),
                'chroma':chroma.tolist()
            }, h)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--music_type', type=str)
    parser.add_argument('--music_dir', type=str)
    parser.add_argument('--acoustic_feature_dir', type=str)
    
    args = parser.parse_args()
    extract_acoustic_feature(args)