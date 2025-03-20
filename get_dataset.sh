#!/bin/bash
# Script to fetch and unzip the available data.
# It uses config as the configuration file (duh!)
echo "Reading configuration from ./config....." >&2
source ./config
if [[ $ready_to_download -eq 0 ]]; then
  echo "Please read the documentation and edit the config file accordingly." >&2
  exit 1
fi
if [ ! -d "$destination" ]; then
    mkdir "$destination"
fi
seq_sets=('imageSequence')
if [[ $download_masks -eq 1 ]]; then
   seq_sets=('imageSequence' 'FGmasks' 'ChairMasks')
fi
source_path="http://gvv.mpi-inf.mpg.de/3dhp-dataset"
echo "Download destination set to $destination " >&2

for subject in ${subjects[@]}; do
  # Format subject number with leading zero
  subject_padded=$(printf "%02d" $subject)
  subject_dir="subject_$subject_padded"

  if [ ! -d "$destination/$subject_dir" ]; then
      mkdir "$destination/$subject_dir"
  fi
  for seq in 1 2; do
      # Format sequence number with leading zero
      seq_padded=$(printf "%02d" $seq)
      seq_dir="sequence_$seq_padded"

      if [ ! -d "$destination/$subject_dir/$seq_dir" ]; then
          mkdir "$destination/$subject_dir/$seq_dir"
      fi
      echo "Downloading Subject $subject, Sequence $seq ... " >&2

      # Note: We still use original naming for the download URLs
      wget "$source_path/S$subject/Seq$seq/annot.mat"
      mv "./annot.mat" "$destination/$subject_dir/$seq_dir/annot.mat"
      wget "$source_path/S$subject/Seq$seq/camera.calibration"
      mv "./camera.calibration" "$destination/$subject_dir/$seq_dir/camera.calibration"

    #Download the videos first, and then unzip them
    for im in "${seq_sets[@]}"; do
      echo "... $im ... " >&2
      if [ ! -d "$destination/$subject_dir/$seq_dir/$im" ]; then
          mkdir "$destination/$subject_dir/$seq_dir/$im"
      fi
      if [ ! -f "$destination/$subject_dir/$seq_dir/$im/vnect_cameras.zip" ]; then
          wget "$source_path/S$subject/Seq$seq/$im/vnect_cameras.zip"
          mv "./vnect_cameras.zip" "$destination/$subject_dir/$seq_dir/$im/vnect_cameras.zip"
      fi
      if [ $download_extra_wall_cameras -ne 0 ]; then
          if [ ! -f "$destination/$subject_dir/$seq_dir/$im/other_angled_cameras.zip" ]; then
              wget "$source_path/S$subject/Seq$seq/$im/other_angled_cameras.zip"
              mv "./other_angled_cameras.zip" "$destination/$subject_dir/$seq_dir/$im/other_angled_cameras.zip"
          fi
      fi
      if [ $download_extra_ceiling_cameras -ne 0 ]; then
          if [ ! -f "$destination/$subject_dir/$seq_dir/$im/ceiling_cameras.zip" ]; then
              wget "$source_path/S$subject/Seq$seq/$im/ceiling_cameras.zip"
              mv "./ceiling_cameras.zip" "$destination/$subject_dir/$seq_dir/$im/ceiling_cameras.zip"
          fi
      fi
    done

    #Unzip the videos now
    for im in "${seq_sets[@]}"; do
      echo "... $im ... " >&2
      if [ ! -d "$destination/$subject_dir/$seq_dir/$im" ]; then
          mkdir "$destination/$subject_dir/$seq_dir/$im"
      fi
      if [ -f "$destination/$subject_dir/$seq_dir/$im/vnect_cameras.zip" ]; then
          unzip -j "$destination/$subject_dir/$seq_dir/$im/vnect_cameras.zip" -d "$destination/$subject_dir/$seq_dir/$im/"
          rm "$destination/$subject_dir/$seq_dir/$im/vnect_cameras.zip"
      fi
      if [ -f "$destination/$subject_dir/$seq_dir/$im/other_angled_cameras.zip" ]; then
          unzip -j "$destination/$subject_dir/$seq_dir/$im/other_angled_cameras.zip" -d "$destination/$subject_dir/$seq_dir/$im/"
          rm "$destination/$subject_dir/$seq_dir/$im/other_angled_cameras.zip"
      fi
      if [ -f "$destination/$subject_dir/$seq_dir/$im/ceiling_cameras.zip" ]; then
          unzip -j "$destination/$subject_dir/$seq_dir/$im/ceiling_cameras.zip" -d "$destination/$subject_dir/$seq_dir/$im/"
          rm "$destination/$subject_dir/$seq_dir/$im/ceiling_cameras.zip"
      fi
    done

  done #Seq
done #Subject