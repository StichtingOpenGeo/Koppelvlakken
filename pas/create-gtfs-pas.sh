#!/bin/bash

DATE=$(date +'%Y%m%d')
rm /tmp/*.txt

cp linepublicnumbers.csv /tmp
psql -d $1 -f pas-gtfs.sql
zip -j gtfs-pasret-$DATE.zip /tmp/*.txt
