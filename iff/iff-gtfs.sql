create table dataownerurl (company integer primary key, agency_url varchar(50));
insert into dataownerurl values (22, 'http://www.gvb.nl');
insert into dataownerurl values (911, 'http://www.veolia.nl');
insert into dataownerurl values (500, 'http://www.arriva.nl');
insert into dataownerurl values (23, 'http://www.htm.nl');
insert into dataownerurl values (600, 'http://www.connexxion.nl');
insert into dataownerurl values (805, 'http://www.connexxion.nl');
insert into dataownerurl values (24, 'http://www.ret.nl');
insert into dataownerurl values (980, 'http://www.sncf.fr');
insert into dataownerurl values (910, 'http://www.db.de');
insert into dataownerurl values (920, 'http://www.nmbs.be');
insert into dataownerurl values (700, 'http://www.veolia.nl');
insert into dataownerurl values (701, 'http://www.veolia.nl');
insert into dataownerurl values (35, 'http://www.ebs-ov.nl');
insert into dataownerurl values (400, 'http://www.syntus.nl');
insert into dataownerurl values (750, 'http://www.qbuzz.nl');
insert into dataownerurl values (100, 'http://www.ns.nl');
insert into dataownerurl values (37, 'http://www.ns.nl');
insert into dataownerurl values (25, 'http://www.ns.nl');
insert into dataownerurl values (200, 'http://www.ns-hispeed.nl');
insert into dataownerurl values (960, 'http://www.ns-hispeed.nl');
insert into dataownerurl values (300, 'http://www.thalys.nl');

COPY(
SELECT
c.company as agency_id,
name as agency_name,
agency_url,
'Europe/Amsterdam' AS agency_timezone,
'nl' AS agency_lang
FROM
company as c, dataownerurl as d
WHERE c.company = d.company
) TO '/tmp/agency.txt' WITH CSV HEADER;

COPY (
SELECT
'OVapi' as feed_publisher_name,
'http://ovapi.nl/' as feed_publisher_url,
'nl' as feed_lang,
replace(cast(firstday AS text), '-', '') as feed_start_date,
replace(cast(lastday AS text), '-', '') as feed_end_date,
now() as feed_version
FROM delivery
) TO '/tmp/feed_info.txt' WITH CSV HEADER;

COPY (
SELECT
footnote as service_id,
replace(cast(servicedate as text), '-', '') as date,
'1' as exception_type
FROM footnote
) TO '/tmp/calendar_dates.txt' WITH CSV HEADER;

alter table station add column the_geom geometry;
update station set the_geom = ST_Transform(st_setsrid(st_makepoint(x,y), 28992), 4326) WHERE x is not null and y is not null; 
update station set the_geom = st_setsrid(st_makepoint(5.317222,43.455), 4326) where shortname = 'aixtgv';
update station set the_geom = st_setsrid(st_makepoint(8.469858,49.479633), 4326) where shortname = 'mannhe';
update station set the_geom = st_setsrid(st_makepoint(11.627778,52.130556), 4326) where shortname = 'magdeb';

COPY(
SELECT
shortname as stop_id,
shortname as stop_code,
name as stop_name,
CAST(st_X(the_geom) AS NUMERIC(8,5)) AS stop_lon,
CAST(st_Y(the_geom) AS NUMERIC(9,6)) AS stop_lat,
CASE WHEN (timezone = 1) THEN  'Europe/London' ELSE 'Europe/Amsterdam' END AS stop_timezone,
1      AS location_type,
NULL   AS parent_station,
NULL   AS platform_code
FROM
(SELECT * from station where shortname in (select distinct station from timetable_stop)) as x
UNION
SELECT
shortname||'|'||COALESCE(departure,'0') as stop_id,
NULL as stop_code,
CASE WHEN (departure is not null) THEN name||' Perron '||departure ELSE name END as stop_name,
COALESCE(CAST(st_X(the_geom) AS NUMERIC(8,5)),0) AS stop_lon,
COALESCE(CAST(st_Y(the_geom) AS NUMERIC(9,6)),0) AS stop_lat,
NULL as stop_timezone,
0      AS location_type,
shortname   AS parent_station,
departure   AS platform_code
FROM
(SELECT * from station as s,timetable_platform as p where p.station = s.shortname and shortname in (select distinct station from timetable_stop)) as x
UNION
SELECT
shortname||'|0' as stop_id,
NULL as stop_code,
name as stop_name,
COALESCE(CAST(st_X(the_geom) AS NUMERIC(8,5)),0) AS stop_lon,
COALESCE(CAST(st_Y(the_geom) AS NUMERIC(9,6)),0) AS stop_lat,
NULL as stop_timezone,
0      AS location_type,
shortname   AS parent_station,
NULL   AS platform_code
FROM
(SELECT * from station as s WHERE shortname in (select distinct station from timetable_stop)) as x
) TO '/tmp/stops.txt' WITH CSV HEADER;

COPY (
SELECT DISTINCT ON (transmode,companynumber,description)
companynumber||'-'||transmode as route_id,
companynumber as agency_id,
null as route_short_name,
description as route_long_name,
CASE WHEN (transmode = 'NSS' or transmode = 'NSB' or transmode = 'B') THEN 3 
     WHEN (transmode = 'NSM') THEN 1 
     WHEN (transmode = 'NST') THEN 0
     ELSE 2 END as route_type
FROM timetable_transport as t,trnsmode as m,timetable_service as s
WHERE m.code = t.transmode and t.serviceid = s.serviceid
) TO '/tmp/routes.txt' WITH CSV HEADER;

update timetable_service set servicenumber = 0 where servicenumber is null and variant is null;
update timetable_transport set laststop = 999 where serviceid not in (select serviceid from timetable_transport group by serviceid having count(*) > 1);

COPY(
SELECT
companynumber||'-'||transmode as route_id,
footnote as service_id,
service.serviceid||'|'||footnote||'|'||COALESCE(servicenumber,cast (variant as integer)) as trip_id,
name as trip_headsign,
COALESCE(servicenumber,cast (variant as integer))%2 as direction_id,
COALESCE(servicenumber,cast (variant as integer)) as journeycode,
service.serviceid as block_id
FROM
timetable_service as service,timetable_validity as validity,timetable_transport as trans, station,
(select serviceid,station,row_number() over (partition by serviceid) as service_seq from timetable_stop) as stops
WHERE
validity.serviceid = service.serviceid AND
((validity.laststop = service.laststop AND validity.firststop = service.firststop) or validity.laststop = 999 ) AND
trans.serviceid = service.serviceid AND 
((trans.laststop = service.laststop AND trans.firststop = service.firststop) or trans.laststop = 999) AND
footnote is not null AND
stops.serviceid = service.serviceid AND
stops.service_seq = service.laststop AND
stops.station = station.shortname AND
service.serviceid not in (select serviceid from timetable_attribute where code = 'NIIN')
ORDER BY trip_id
) TO '/tmp/trips.txt' WITH CSV HEADER;

copy (
SELECT
trip_id,
CASE WHEN(stop_sequence = 1) THEN departure_time ELSE arrival_time END,
departure_time,
stop_id,
stop_sequence,
arrival_platform,
pickup_type
FROM
	(SELECT
	service.serviceid||'|'||validity.footnote||'|'||COALESCE(servicenumber,cast (variant as integer)) as trip_id,
	arrivaltime as arrival_time,
	COALESCE(departuretime,arrivaltime) as departure_time,
	stop.station||'|'||COALESCE(departure,'0') as stop_id,
        row_number() over (partition by service.serviceid,validity.footnote,COALESCE(servicenumber,cast (variant as integer)) order by idx asc) as stop_sequence,
	CASE WHEN (arrival <> departure) THEN arrival else NULL END as arrival_platform,
        idx,
        CASE WHEN (service.serviceid in (select serviceid from timetable_attribute where code = 'RESV')) THEN 2 ELSE 0 END as pickup_type
	FROM
	timetable_service as service,
        timetable_validity as validity,
        timetable_stop as stop
        LEFT JOIN timetable_platform as platform USING (serviceid,idx)
	WHERE
        idx between service.firststop and service.laststop AND
        stop.serviceid = service.serviceid AND
        validity.serviceid = service.serviceid AND
        validity.footnote is not null AND
        service.serviceid not in (select serviceid from timetable_attribute where code = 'NIIN')
	) as x
ORDER BY trip_id,stop_sequence
) TO '/tmp/stop_times.txt' WITH CSV HEADER;
