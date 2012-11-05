#!/bin/bash
DBNAME=iff
DATE=$(date +'%Y%m%d')
rm /tmp/*.txt

dropdb $DBNAME
createdb $DBNAME
psql -d $DBNAME -c "create extension postgis;"
python parser.py $1
psql -d $DBNAME -f iff.sql
cp stops_positioned.txt /tmp
psql -d $DBNAME -f iff-gtfs.sql
zip -j gtfs-iffns-$DATE.zip /tmp/*.txt
