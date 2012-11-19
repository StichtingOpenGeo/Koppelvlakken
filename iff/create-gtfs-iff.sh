#!/bin/bash

DATE=$(date +'%Y%m%d')
rm /tmp/*.txt

cp stops_positioned.txt /tmp
psql -d $1 -f iff-gtfs.sql
zip -j gtfs-iffns-$DATE.zip /tmp/*.txt
