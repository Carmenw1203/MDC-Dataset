# The Multi-Dancer Choreography dataset (MDC)

Paper: GroupDancer: Music to Multi-People Dance Synthesis with Style Collaboration

## Dataset overview

We organizes the files as follows:

```
|── README.md
|── data
|    |── dancer_choreo_json: annotations of dancer arrangement
|    |── motion_choreo_json: annotations of motion choreography for each dancer
|    |── motion_fbx: raw motion files in .fbx format
|    |── motion_unit_csv: annotations of motion unit for each dancer
|    |── music
|── fbx_model
|── scripts
|── sh
|── requirements.txt
```

## Requirements
* Python 3.7+
* [Python FBX](https://download.autodesk.com/us/fbx/20112/fbx_sdk_help/index.html?url=WS1a9193826455f5ff453265c9125faa23bbb5fe8.htm,topicNumber=d0e8312)

## Visualize Raw Data
### 1. Download Data
Download link:
```
Google Drive: https://drive.google.com/file/d/1Q2SnPrlVM_U8wSJI-0JTVJH0bemCfj3U/view?usp=drive_link
```
unzip it under the `data` directory
### 2. Install with pip
```
pip install -r requirements.txt
```
### 3. Extract Acoustic Features
```
bash sh/extract_acoustic_feature.sh
```
### 4. Read .fbx files and save as .json
```
bash sh/extract_acoustic_feature.sh
```
### 5. Stitch Motion Unit
```
bash sh/stitch_visualize.sh
```
### 6. Save Results as .fbx
```
bash sh/json2fbx.sh
```
Then you can review the raw data under `output_fbx/` with [FBX Review](https://www.autodesk.com/products/fbx/fbx-review)

## Citation
```
@inproceedings{wang2022groupdancer,
  title={Groupdancer: Music to multi-people dance synthesis with style collaboration},
  author={Wang, Zixuan and Jia, Jia and Wu, Haozhe and Xing, Junliang and Cai, Jinghe and Meng, Fanbo and Chen, Guowen and Wang, Yanfeng},
  booktitle={Proceedings of the 30th ACM International Conference on Multimedia},
  pages={1138--1146},
  year={2022}
}
```