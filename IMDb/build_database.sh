#!/bin/sh

# Download datasets
wget https://datasets.imdbws.com/name.basics.tsv.gz
wget https://datasets.imdbws.com/title.akas.tsv.gz
wget https://datasets.imdbws.com/title.basics.tsv.gz
wget https://datasets.imdbws.com/title.crew.tsv.gz
wget https://datasets.imdbws.com/title.episode.tsv.gz
wget https://datasets.imdbws.com/title.principals.tsv.gz
wget https://datasets.imdbws.com/title.ratings.tsv.gz

# Create database
sudo apt install postgresql
sudo service postgresql start
sudo -u postgres psql -c 'create database imdb;'
sudo -u postgres psql -c 'create user admin with encrypted password toor;'
sudo -u postgres psql -c 'grant all privileges on database imdb to admin;'

# Populate database with downloaded datasets
s32cinemagoer.py . postgresql://admin:toor@localhost/imdb