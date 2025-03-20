import argparse
import json
from pathlib import Path

import scipy.io as sio


def extract_all_joints(dataset_path, subject_id, sequence_id):
    """Extract all joint positions from annotation files and save as JSON for each camera."""
    # Convert to Path objects
    dataset_path = Path(dataset_path)

    # Path to the annotation file
    annot_path = dataset_path / f'subject_{subject_id:02d}/sequence_{sequence_id:02d}/annot.mat'
    frames_base_dir = dataset_path / f'frames/subject_{subject_id:02d}/sequence_{sequence_id:02d}/'

    # Load annotation data
    print(f"Loading annotations from {annot_path}...")
    annot_data = sio.loadmat(annot_path)

    # Get number of frames
    frames = annot_data['frames'].flatten()
    n_frames = len(frames)
    print(f"Found {n_frames} frames")

    # Define all joint names (from mpii_get_joint_set.m)
    joint_names = [
        'spine3', 'spine4', 'spine2', 'spine', 'pelvis',
        'neck', 'head', 'head_top', 'left_clavicle', 'left_shoulder', 'left_elbow',
        'left_wrist', 'left_hand', 'right_clavicle', 'right_shoulder', 'right_elbow', 'right_wrist',
        'right_hand', 'left_hip', 'left_knee', 'left_ankle', 'left_foot', 'left_toe',
        'right_hip', 'right_knee', 'right_ankle', 'right_foot', 'right_toe'
    ]
    n_joints = len(joint_names)
    print(f"Extracting data for {n_joints} joints")

    # Number of cameras
    n_cameras = annot_data['annot2'].shape[0]
    print(f"Found {n_cameras} cameras")

    # Process for each camera
    for cam_idx in range(n_cameras):
        camera_dir = frames_base_dir / f'camera_{cam_idx:02d}'

        # Skip cameras that don't have a directory
        if not camera_dir.exists():
            print(f"Skipping camera {cam_idx} - directory does not exist: {camera_dir}")
            continue

        print(f"Processing camera {cam_idx}...")

        # Process each frame for this camera
        for frame_idx in range(n_frames):
            # Initialize data for this frame
            frame_data = {
                'frame': int(frames[frame_idx]),
                'camera_id': cam_idx,
                'joints': {}
            }

            # Process each joint
            for joint_idx in range(n_joints):
                joint_name = joint_names[joint_idx]

                # 2D image coordinates (annot2)
                joint_2d_x = float(annot_data['annot2'][cam_idx, 0][frame_idx, joint_idx*2])
                joint_2d_y = float(annot_data['annot2'][cam_idx, 0][frame_idx, joint_idx*2 + 1])

                # 3D camera coordinates (annot3)
                joint_3d_cam_x = float(annot_data['annot3'][cam_idx, 0][frame_idx, joint_idx*3])
                joint_3d_cam_y = float(annot_data['annot3'][cam_idx, 0][frame_idx, joint_idx*3 + 1])
                joint_3d_cam_z = float(annot_data['annot3'][cam_idx, 0][frame_idx, joint_idx*3 + 2])

                # 3D world coordinates (univ_annot3)
                joint_3d_world_x = float(annot_data['univ_annot3'][cam_idx, 0][frame_idx, joint_idx*3])
                joint_3d_world_y = float(annot_data['univ_annot3'][cam_idx, 0][frame_idx, joint_idx*3 + 1])
                joint_3d_world_z = float(annot_data['univ_annot3'][cam_idx, 0][frame_idx, joint_idx*3 + 2])

                # Add joint data
                frame_data['joints'][joint_name] = {
                    '2d': [joint_2d_x, joint_2d_y],
                    '3d_camera': [joint_3d_cam_x, joint_3d_cam_y, joint_3d_cam_z],
                    '3d_world': [joint_3d_world_x, joint_3d_world_y, joint_3d_world_z]
                }

            # Save frame data as JSON
            output_file = camera_dir / f"frame_{frame_idx:06d}.json"
            with open(output_file, 'w') as f:
                json.dump(frame_data, f, indent=2)

            # Print progress
            if frame_idx % 500 == 0 and frame_idx > 0:
                print(f"  Camera {cam_idx}: Processed {frame_idx}/{n_frames} frames")

        print(f"  Camera {cam_idx}: Completed all {n_frames} frames")

    print(f"Finished extracting joint positions for subject {subject_id}, sequence {sequence_id}")


def discover_subjects_and_sequences(dataset_path):
    """Dynamically discover available subjects and sequences in the dataset."""
    dataset_path = Path(dataset_path)
    subjects_and_sequences = []

    # Find all subject directories
    for subject_dir in dataset_path.glob('subject_*'):
        if not subject_dir.is_dir():
            continue

        # Extract subject ID from the directory name
        subject_id_str = subject_dir.name.split('_')[-1]
        try:
            subject_id = int(subject_id_str)

            # Find all sequence directories for this subject
            for sequence_dir in subject_dir.glob('sequence_*'):
                if not sequence_dir.is_dir():
                    continue

                # Check if annot.mat exists
                if (sequence_dir / 'annot.mat').exists():
                    # Extract sequence ID from the directory name
                    sequence_id_str = sequence_dir.name.split('_')[-1]
                    try:
                        sequence_id = int(sequence_id_str)
                        subjects_and_sequences.append((subject_id, sequence_id))
                    except ValueError:
                        print(f"Skipping invalid sequence directory: {sequence_dir}")
                else:
                    print(f"Skipping directory without annot.mat: {sequence_dir}")
        except ValueError:
            print(f"Skipping invalid subject directory: {subject_dir}")

    return subjects_and_sequences


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Extract all joint positions from MPI-INF-3DHP dataset')
    parser.add_argument('--dataset_path', type=str, help='Path to the MPI-INF-3DHP dataset', default="./")
    args = parser.parse_args()

    dataset_path = Path(args.dataset_path)

    # Verify that the dataset path exists
    if not dataset_path.exists():
        print(f"Error: Dataset path does not exist: {dataset_path}")
        return

    # Discover available subjects and sequences
    subjects_and_sequences = discover_subjects_and_sequences(dataset_path)

    if not subjects_and_sequences:
        print(f"Error: No valid subjects and sequences found in {dataset_path}")
        return

    print(f"Found {len(subjects_and_sequences)} subject/sequence combinations:")
    for subject_id, sequence_id in subjects_and_sequences:
        print(f"  - Subject {subject_id:02d}, Sequence {sequence_id:02d}")

    # Process each subject and sequence
    for subject_id, sequence_id in subjects_and_sequences:
        extract_all_joints(dataset_path, subject_id, sequence_id)

    print("All joint positions extracted successfully!")


if __name__ == "__main__":
    main()