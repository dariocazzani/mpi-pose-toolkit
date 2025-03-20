# MPI-INF-3DHP Dataset Processing Tools

Simple tools to download, organize and process the MPI-INF-3DHP human pose estimation dataset.

## Requirements

- Python 3.6+
- Required Python packages: `scipy`, `numpy`
- `ffmpeg` for frame extraction
- Approximately 25GB of disk space for the complete training set

## Quick Start

1. **Download and organize the dataset:**
   ```bash
   ./get_dataset.sh
   ```

2. **Extract frames from videos:**
   ```bash
   ./extract_frames.sh --fps 0  # Extract all frames
   # OR
   ./extract_frames.sh --fps 1  # Extract 1 frame per second
   ```

3. **Extract joint positions:**
   ```bash
   python extract_joints.py
   ```

4. **Clean up unmatched JSON files:**
   ```bash
   python clean_landmarks.py
   ```

5. **[Optional] Clean up original dataset files:**
   ```bash
   ./cleanup.sh
   ```

## What These Scripts Do

- **get_dataset.sh**: Downloads the MPI-INF-3DHP dataset and organizes files into a clean structure with subject_XX and sequence_XX folders
- **extract_frames.sh**: Extracts frames from videos into JPG files with `--fps` option to control frame rate
- **extract_joints.py**: Processes annotation files to extract 3D joint positions for each frame
- **clean_landmarks.py**: Ensures joint annotation files match extracted frames
- **cleanup.sh**: [Optional] Removes original subject directories and util folders after processing to save disk space

## Dataset Structure After Processing

```
./
├── frames/
│   ├── subject_01/
│   │   ├── sequence_01/
│   │   │   ├── camera_01/
│   │   │   │   ├── frame_000001.jpg
│   │   │   │   ├── frame_000001.json
│   │   │   │   └── ...
│   │   │   └── ...
│   │   └── ...
│   └── ...
```

## About the Dataset

The MPI-INF-3DHP dataset is designed for 3D human pose estimation from monocular RGB images. It provides greater diversity in pose, human appearance, clothing, occlusion, and viewpoints than previous datasets.

For more information, visit the [official dataset page](https://vcai.mpi-inf.mpg.de/3dhp-dataset/).

## Citation

If you use this dataset in your research, please cite:

```bibtex
@inproceedings{mono-3dhp2017,
 author = {Mehta, Dushyant and Rhodin, Helge and Casas, Dan and Fua, Pascal and Sotnychenko, Oleksandr and Xu, Weipeng and Theobalt, Christian},
 title = {Monocular 3D Human Pose Estimation In The Wild Using Improved CNN Supervision},
 booktitle = {3D Vision (3DV), 2017 Fifth International Conference on},
 url = {http://gvv.mpi-inf.mpg.de/3dhp_dataset},
 year = {2017},
 organization={IEEE},
 doi={10.1109/3dv.2017.00064},
}
```
