-- make sure to copy linepublicnumbers.csv to tmp
create table linepublicnumber (lijnsysteemnr varchar(3), linepublicnumber varchar(10));
copy linepublicnumber from '/tmp/linepublicnumbers.csv' CSV;

--Delete some timingpoints that are not userstops (?)
delete from stops where naam like '%Remise%' or naam like '%Garage%';

COPY(
SELECT
'000024' as agency_id,
'RET' as agency_name,
'http://www.ret.nl' as agency_url,
'Europe/Amsterdam' AS agency_timezone,
'nl' AS agency_lang
) TO '/tmp/agency.txt' WITH CSV HEADER;

COPY (
SELECT
'OVapi' as feed_publisher_name,
'http://ovapi.nl/' as feed_publisher_url,
'nl' as feed_lang,
replace(cast(min(datum) AS text), '-', '') as feed_start_date,
replace(cast(max(datum) AS text), '-', '') as feed_end_date,
now() as feed_version
FROM voetnoot
) TO '/tmp/feed_info.txt' WITH CSV HEADER;

COPY (
SELECT
voetnoot as service_id,
replace(cast(datum as text), '-', '') as date,
'1' as exception_type
FROM voetnoot
) TO '/tmp/calendar_dates.txt' WITH CSV HEADER;

COPY(
SELECT
halteid as stop_id,
naam as stop_name,
CAST(st_Y(the_geom) AS NUMERIC(9,6)) AS stop_lat,
CAST(st_X(the_geom) AS NUMERIC(8,5)) AS stop_lon
FROM
(select *,ST_Transform(st_setsrid(st_makepoint(x,y), 28992), 4326) as the_geom from stops) as x
) TO '/tmp/stops.txt' WITH CSV HEADER;

create table gtfs_route_type (modaliteit varchar(1) primary key, route_type int4);
insert into gtfs_route_type values ('T', 0);
insert into gtfs_route_type values ('M', 1);
insert into gtfs_route_type values ('B', 3);
insert into gtfs_route_type values ('H', 3);
insert into gtfs_route_type values ('F', 4);

COPY (
SELECT DISTINCT ON (lijnsysteemnr)
lijnsysteemnr as route_id,
vervoerdercode as agency_id,
linepublicnumber as route_short_name,
NULL as route_long_name,
route_type
FROM gtfs_route_type as g,  pujo as p LEFT JOIN linepublicnumber as l using (lijnsysteemnr)
WHERE p.modaliteit = g.modaliteit
) TO '/tmp/routes.txt' WITH CSV HEADER;


COPY(
SELECT
p.lijnsysteemnr as route_id,
voetnoot as service_id,
voetnoot||'|'||p.ritnummer as trip_id,
naam as trip_headsign,
(p.richting - 1) as direction_id,
p.ritnummer as journeycode
FROM
pujo as p,
(
	SELECT x.vervoerdercode,x.lijnsysteemnr,x.richting,x.ritnummer,x.halteid
	FROM pujopass as x ,(
	select vervoerdercode,lijnsysteemnr,richting,ritnummer,max(p1.stopsequentie) as stopsequentie
	FROM pujopass as p1
	GROUP BY vervoerdercode,lijnsysteemnr,richting,ritnummer) as y
        where x.vervoerdercode = y.vervoerdercode AND x.lijnsysteemnr = y.lijnsysteemnr AND x.richting = y.richting AND x.ritnummer = y.ritnummer AND x.stopsequentie = y.stopsequentie
) as e,
(SELECT halteid,naam FROM STOPS) as haltes
WHERE
p.vervoerdercode = e.vervoerdercode AND
p.lijnsysteemnr = e.lijnsysteemnr AND
p.richting = e.richting AND
p.ritnummer = e.ritnummer AND
e.halteid = haltes.halteid
) TO '/tmp/trips.txt' WITH CSV HEADER;

copy (
SELECT
voetnoot||'|'||p.ritnummer as trip_id,
COALESCE(aankomsttijd,vertrektijd) as arrival_time,
COALESCE(vertrektijd,aankomsttijd) as departure_time,
halteid as stop_id,
stopsequentie as stop_sequence
FROM pujopass as p
ORDER BY trip_id,stop_sequence
) TO '/tmp/stop_times.txt' WITH CSV HEADER;
