#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo."
    exit
fi

declare -a dependencies=(
    # db-interface, backend:
    pipenv
    
    # frontend:
    npm

    # cypress:
    libgtk2.0-0
    libgtk-3-0
    libgbm-dev
    libnotify-dev
    libgconf-2-4
    libnss3
    libxss1
    libasound2
    libxtst6
    xauth
    xvfb
)

apt-get install "${dependencies[@]}"