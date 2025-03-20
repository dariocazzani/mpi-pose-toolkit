#!/usr/bin/env python3
import argparse
import json
import random
from pathlib import Path

import cv2


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Visualize joint annotations on images')
    parser.add_argument('--shuffle', action='store_true',
                        help='Shuffle images for random visualization')
    parser.add_argument('--dataset_path', type=str, default='./',
                        help='Path to the dataset root directory')
    args = parser.parse_args()

    # Define the dataset path
    dataset_path = Path(args.dataset_path)
    frames_dir = dataset_path / 'frames'

    if not frames_dir.exists():
        print(f"Error: Frames directory not found: {frames_dir}")
        return

    # Define joint connections for skeleton visualization
    # Format: [(joint_name1, joint_name2, color), ...]
    joint_connections = [
        # Torso (green)
        ('pelvis', 'spine', (0, 255, 0)),
        ('spine', 'spine2', (0, 255, 0)),
        ('spine2', 'spine3', (0, 255, 0)),
        ('spine3', 'spine4', (0, 255, 0)),
        ('spine4', 'neck', (0, 255, 0)),

        # Head (yellow)
        ('neck', 'head', (0, 255, 255)),
        ('head', 'head_top', (0, 255, 255)),

        # Left arm (red)
        ('spine4', 'left_clavicle', (255, 0, 0)),
        ('left_clavicle', 'left_shoulder', (255, 0, 0)),
        ('left_shoulder', 'left_elbow', (255, 0, 0)),
        ('left_elbow', 'left_wrist', (255, 0, 0)),
        ('left_wrist', 'left_hand', (255, 0, 0)),

        # Right arm (blue)
        ('spine4', 'right_clavicle', (0, 0, 255)),
        ('right_clavicle', 'right_shoulder', (0, 0, 255)),
        ('right_shoulder', 'right_elbow', (0, 0, 255)),
        ('right_elbow', 'right_wrist', (0, 0, 255)),
        ('right_wrist', 'right_hand', (0, 0, 255)),

        # Left leg (magenta)
        ('pelvis', 'left_hip', (255, 0, 255)),
        ('left_hip', 'left_knee', (255, 0, 255)),
        ('left_knee', 'left_ankle', (255, 0, 255)),
        ('left_ankle', 'left_foot', (255, 0, 255)),
        ('left_foot', 'left_toe', (255, 0, 255)),

        # Right leg (cyan)
        ('pelvis', 'right_hip', (255, 255, 0)),
        ('right_hip', 'right_knee', (255, 255, 0)),
        ('right_knee', 'right_ankle', (255, 255, 0)),
        ('right_ankle', 'right_foot', (255, 255, 0)),
        ('right_foot', 'right_toe', (255, 255, 0))
    ]

    # Find all image and JSON pairs
    image_json_pairs = []

    for camera_dir in frames_dir.glob('*/*/camera_*'):
        if not camera_dir.is_dir():
            continue

        for img_file in camera_dir.glob('frame_*.jpg'):
            json_file = img_file.with_suffix('.json')
            if json_file.exists():
                image_json_pairs.append((img_file, json_file))

    if not image_json_pairs:
        print("No image-JSON pairs found!")
        return

    print(f"Found {len(image_json_pairs)} image-JSON pairs")

    # Shuffle if requested
    if args.shuffle:
        random.shuffle(image_json_pairs)
        print("Images shuffled for random viewing")
    else:
        # Sort by path
        image_json_pairs.sort(key=lambda x: str(x[0]))
        print("Images sorted by path")

    # Display help message
    print("\nVisualization Controls:")
    print("  Space: Next image")
    print("  Q: Quit")

    # Process and display images
    total_images = len(image_json_pairs)
    for idx, (img_path, json_path) in enumerate(image_json_pairs):
        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Error loading image: {img_path}")
            continue

        # Load joint data
        try:
            with open(json_path, 'r') as f:
                joint_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {json_path} - {e}")
            continue

        # Draw skeleton
        draw_skeleton(img, joint_data, joint_connections)

        # Show image info
        subject_seq_cam = f"{img_path.parent.parent.parent.name}/{img_path.parent.parent.name}/{img_path.parent.name}"
        frame_num = img_path.stem

        # Display image with info and progress
        cv2.putText(img, f"{subject_seq_cam} - {frame_num}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(img, f"{subject_seq_cam} - {frame_num}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        progress_text = f"Image {idx+1} of {total_images}"
        cv2.putText(img, progress_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(img, progress_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        # Resize if image is too large
        h, w = img.shape[:2]
        max_height = 800
        max_width = 1200

        if h > max_height or w > max_width:
            # Calculate scale factor to fit within max dimensions
            scale = min(max_height / h, max_width / w)
            new_h, new_w = int(h * scale), int(w * scale)
            img_display = cv2.resize(img, (new_w, new_h))
        else:
            img_display = img

        cv2.imshow('Joint Visualization', img_display)

        # Wait for key press, exit if 'q' is pressed
        key = cv2.waitKey(0)
        if key == ord('q') or key == 27:  # q or ESC
            break

    cv2.destroyAllWindows()

def draw_skeleton(img, joint_data, joint_connections):
    """Draw the skeleton on the image"""
    joints = joint_data['joints']

    # Draw connections
    for start_joint, end_joint, color in joint_connections:
        if start_joint in joints and end_joint in joints:
            start_pos = joints[start_joint]['2d']
            end_pos = joints[end_joint]['2d']

            # Convert to integer pixel coordinates
            start_x, start_y = int(start_pos[0]), int(start_pos[1])
            end_x, end_y = int(end_pos[0]), int(end_pos[1])

            # Draw line if the points are valid
            if min(start_x, start_y, end_x, end_y) > 0:
                cv2.line(img, (start_x, start_y), (end_x, end_y), color, 2)

    # Draw joints
    for joint_name, joint_info in joints.items():
        pos_2d = joint_info['2d']
        x, y = int(pos_2d[0]), int(pos_2d[1])

        # Draw a circle at joint position if valid
        if x > 0 and y > 0:
            cv2.circle(img, (x, y), 5, (0, 0, 0), -1)  # Black outline
            cv2.circle(img, (x, y), 3, (255, 255, 255), -1)  # White center

if __name__ == "__main__":
    main()