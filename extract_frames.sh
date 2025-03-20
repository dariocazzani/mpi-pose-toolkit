#!/bin/bash

# Check for the required --fps parameter
if [[ "$1" != "--fps" || -z "$2" || ("$2" != "0" && "$2" != "1") ]]; then
  echo "Usage: $0 --fps [0|1] [dataset_directory]"
  echo "  --fps 0: Extract all frames"
  echo "  --fps 1: Extract one frame per second"
  exit 1
fi

FPS_MODE=$2
shift 2  # Remove the --fps and its value from the arguments

# Make sure we have the absolute path to handle all cases correctly
DATASET_DIR=$(realpath "${1:-.}")
echo "Using dataset directory: $DATASET_DIR"
echo "FPS mode: $FPS_MODE ($([ "$FPS_MODE" -eq 0 ] && echo "all frames" || echo "1 frame per second"))"

# Verify the directory structure
if [ ! -d "$DATASET_DIR" ]; then
  echo "Error: Dataset directory does not exist"
  exit 1
fi

# Check for at least one subject directory
subject_count=$(find "$DATASET_DIR" -maxdepth 1 -type d -name "subject_*" | wc -l)
if [ "$subject_count" -eq 0 ]; then
  echo "Error: No subject directories (subject_01, subject_02, etc.) found in $DATASET_DIR"
  exit 1
fi

# Create frames directory
FRAMES_DIR="$DATASET_DIR/frames"
mkdir -p "$FRAMES_DIR"

# Log file for errors
echo "Starting frame extraction at $(date)"

# Process each subject and sequence
for subject_dir in "$DATASET_DIR"/subject_*; do
  if [ ! -d "$subject_dir" ]; then
    continue
  fi

  subject=$(basename "$subject_dir")
  echo "Processing subject: $subject"

  # Create subject directory in frames
  subject_frames_dir="$FRAMES_DIR/$subject"
  mkdir -p "$subject_frames_dir"

  for seq_dir in "$subject_dir"/sequence_*; do
    if [ ! -d "$seq_dir" ]; then
      continue
    fi

    seq=$(basename "$seq_dir")
    echo "  Processing sequence: $seq"

    # Create sequence directory in frames
    seq_frames_dir="$subject_frames_dir/$seq"
    mkdir -p "$seq_frames_dir"

    # Check for the imageSequence directory
    img_seq_dir="$seq_dir/imageSequence"
    if [ ! -d "$img_seq_dir" ]; then
      echo "    Warning: No imageSequence directory found in $seq_dir"
      continue
    fi

    # Process each video file
    for video_file in "$img_seq_dir"/*.avi; do
      if [ ! -f "$video_file" ]; then
        echo "    Warning: No .avi files found in $img_seq_dir"
        break
      fi

      # Get video name without extension and rename to camera format
      video_name=$(basename "$video_file" .avi)
      camera_id="camera_$(printf "%02d" "${video_name#video_}")"

      # Create camera directory in frames
      camera_frames_dir="$seq_frames_dir/$camera_id"

      # Skip if already processed
      if [ -d "$camera_frames_dir" ] && [ "$(ls -A "$camera_frames_dir" 2>/dev/null)" ]; then
        echo "    Skipping $video_name (already processed as $camera_id)"
        continue
      fi

      # Create directory
      mkdir -p "$camera_frames_dir"

      echo "    Extracting frames from $video_name to $camera_id"

      # Extract all frames
      if ffmpeg -i "$video_file" -q:v 2 "$camera_frames_dir/frame_%06d.jpg" -loglevel error; then
        frame_count=$(ls "$camera_frames_dir" | wc -l)
        echo "    Successfully extracted $frame_count frames from $video_name to $camera_id"

        # If FPS mode is 1, keep only 1 frame per second
        if [ "$FPS_MODE" -eq 1 ]; then
          # Get the video's FPS using ffprobe
          VIDEO_FPS=$(ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "$video_file" | bc -l | xargs printf "%.0f")

          if [ -z "$VIDEO_FPS" ] || [ "$VIDEO_FPS" -eq 0 ]; then
            echo "    Warning: Could not detect FPS for $video_file, assuming 25 FPS"
            VIDEO_FPS=25
          fi

          echo "    Video FPS detected: $VIDEO_FPS, keeping 1 frame per second"

          # Create a temporary file to list frames to keep
          KEEP_LIST=$(mktemp)

          # List all frames with their indices
          find "$camera_frames_dir" -name "frame_*.jpg" | sort > "$KEEP_LIST.all"

          # Keep only 1 frame per second (starting from frame 1, then frame 1+FPS, 1+2*FPS, etc.)
          awk -v fps="$VIDEO_FPS" 'NR == 1 || (NR - 1) % fps == 0' "$KEEP_LIST.all" > "$KEEP_LIST"

          # Calculate frames to delete
          grep -vxFf "$KEEP_LIST" "$KEEP_LIST.all" > "$KEEP_LIST.delete"

          # Delete frames not needed
          delete_count=$(wc -l < "$KEEP_LIST.delete")
          if [ "$delete_count" -gt 0 ]; then
            echo "    Keeping 1 frame per second (deleting $delete_count frames)"
            xargs rm -f < "$KEEP_LIST.delete"
          fi

          # Clean up temporary files
          rm -f "$KEEP_LIST" "$KEEP_LIST.all" "$KEEP_LIST.delete"

          # Recount frames
          kept_frame_count=$(find "$camera_frames_dir" -name "frame_*.jpg" | wc -l)
          echo "    Kept $kept_frame_count frames (1 per second)"
        fi
      else
        echo "    Error extracting frames from $video_file to $camera_id"

        # Clean up empty directory
        if [ -d "$camera_frames_dir" ] && [ -z "$(ls -A "$camera_frames_dir" 2>/dev/null)" ]; then
          rmdir "$camera_frames_dir"
        fi
      fi
    done
  done
done

# Print summary
total_frames=$(find "$FRAMES_DIR" -path "*/camera_*/frame_*.jpg" | wc -l)
echo ""
echo "Frame extraction complete!"
echo "Total frames extracted: $total_frames"