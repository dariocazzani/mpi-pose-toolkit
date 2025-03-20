#!/usr/bin/env python3
import argparse
from pathlib import Path


def clean_unmatched_landmarks(dataset_path):
    """Clean landmark JSON files that don't have matching JPG frames in the same camera directory."""
    dataset_path = Path(dataset_path)
    frames_dir = dataset_path / 'frames'

    if not frames_dir.exists():
        print(f"Error: Frames directory not found: {frames_dir}")
        return

    total_json_removed = 0
    total_jpg_without_json = 0

    # Process each subject directory
    for subject_dir in sorted(frames_dir.glob('subject_*')):
        if not subject_dir.is_dir():
            continue

        subject_id = subject_dir.name
        print(f"Processing {subject_id}...")

        # Process each sequence directory
        for sequence_dir in sorted(subject_dir.glob('sequence_*')):
            if not sequence_dir.is_dir():
                continue

            sequence_id = sequence_dir.name
            print(f"  Processing {sequence_id}...")

            # Process each camera directory
            camera_dirs = sorted([d for d in sequence_dir.glob('camera_*') if d.is_dir()])
            if not camera_dirs:
                print(f"    Warning: No camera directories found in {sequence_dir}")
                continue

            print(f"    Found {len(camera_dirs)} camera directories")

            # Process each camera directory
            for camera_dir in camera_dirs:
                camera_id = camera_dir.name
                print(f"    Processing {camera_id}...")

                # Get all JPG files in this camera
                jpg_files = set(f.stem for f in camera_dir.glob('frame_*.jpg'))

                # Get all JSON files in this camera
                json_files = list(camera_dir.glob('frame_*.json'))

                # Check for JSON files without matching JPGs
                json_removed = 0
                for json_file in json_files:
                    if json_file.stem not in jpg_files:
                        print(f"      Removing {json_file.name} (no matching JPG)")
                        json_file.unlink()
                        json_removed += 1

                # Check for JPGs without matching JSONs
                jpg_without_json = 0
                for jpg_stem in jpg_files:
                    json_path = camera_dir / f"{jpg_stem}.json"
                    if not json_path.exists():
                        jpg_without_json += 1

                total_json_removed += json_removed
                total_jpg_without_json += jpg_without_json

                print(f"      {camera_id}: Removed {json_removed} JSON files without matching JPGs")
                print(f"      {camera_id}: Found {jpg_without_json} JPGs without matching JSONs")

    print("\nSummary:")
    print(f"Total JSON files removed: {total_json_removed}")
    print(f"Total JPG files without matching JSONs: {total_jpg_without_json}")
    print("Landmark cleaning completed!")


def main():
    parser = argparse.ArgumentParser(description='Clean landmark JSON files that have no matching JPG frames')
    parser.add_argument('--dataset_path', type=str, help='Path to the dataset root directory', default="./")
    args = parser.parse_args()

    clean_unmatched_landmarks(args.dataset_path)


if __name__ == "__main__":
    main()