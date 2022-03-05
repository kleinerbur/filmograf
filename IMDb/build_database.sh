#!/bin/bash

if [ `id -u` -ne 0 ]; then
    echo 'Please run this script as root.'
    exit
fi

should_download=1
while getopts "skip" flag
do
    case "${flag}" in
        s) should_download=0;;
    esac
done

# Download datasets
if [ ${should_download} -eq 1 ]; then
    declare -a DATASETS=("name.basics"
        "title.akas"
        "title.basics"
        "title.crew"
        "title.episode"
        "title.principals"
        "title.ratings")
    for dataset in ${DATASETS[*]}; do
        wget -O $dataset.tsv.gz https://datasets.imdbws.com/$dataset.tsv.gz
    done
fi

# Create database
apt install -y postgresql 
service postgresql start
sudo -u postgres psql -c "create database imdb;"
sudo -u postgres psql -c "create user admin with encrypted password 'toor';"
sudo -u postgres psql -c "grant all privileges on database imdb to admin;"

# Populate database with downloaded datasets
apt install -y libpq-dev python-dev
pip3 install psycopg2 Cinemagoer
s32cinemagoer.py . postgresql://admin:toor@localhost/imdb