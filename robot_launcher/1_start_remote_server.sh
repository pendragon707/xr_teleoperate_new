#!/bin/bash

# PC2_USER="unitree"
# PC2_IP="192.168.123.164"
# PC2_PASS="some password" 
# SUDO_PASS="some password" 

# echo "🚀 Starting Image Server on PC2..."

# sshpass -p "$PC2_PASS" ssh -o StrictHostKeyChecking=no "$PC2_USER@$PC2_IP" "
#     echo '$SUDO_PASS' | sudo -S ip link set wlan0 down;
#     source ~/miniconda3/etc/profile.d/conda.sh; # Adjust path if conda is installed elsewhere
#     conda activate teleimager;
#     echo '✅ Server Started';
#     teleimager-server
# "

echo "🚀 Starting Image Server on PC2..."

ssh unitree@192.168.123.164 "
    sudo ip link set wlan0 down;
    conda activate teleimager;
    teleimager-server
"