#!/bin/bash

WORK_DIR="$HOME/Projects/xr_teleoperate/teleop/teleimager" # Adjust to your actual path
CONDA_ENV="tv"

echo "🚀 Starting Local Clients on PC1..."

# Ensure we are in the right directory
cd "$WORK_DIR" || exit

# 1. Open Terminal Tab for Image Client
gnome-terminal --tab --title="Image Client" -- bash -c "
    source ~/miniconda3/etc/profile.d/conda.sh;
    conda activate $CONDA_ENV;
    python -m teleimager.image_client --host 192.168.123.164;
    exec bash
"

# Wait a moment to ensure client binds before starting teleop
sleep 2

WORK_DIR="$HOME/Projects/xr_teleoperate/teleop"
CONDA_ENV="tv"

cd "$WORK_DIR" || exit

# 2. Open Terminal Tab for Teleop Hand/Arm
gnome-terminal --tab --title="Teleop Control" -- bash -c "
    source ~/miniconda3/etc/profile.d/conda.sh;
    conda activate $CONDA_ENV;
    python teleop_hand_and_arm.py --input-mode=controller --arm=G1_29 --ee=dex3 --record --motion --img-server-ip=192.168.123.164 --network-interface=wlo1;
    exec bash
"

echo "✅ All local processes launched."