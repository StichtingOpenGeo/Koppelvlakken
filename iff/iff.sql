create table country(code varchar(4) primary key, inland boolean not null, name varchar(29) not null);
create table company(company integer primary key, code varchar(9) not null, name varchar(29) not null, timeturn time);
create table delivery(company integer references company, firstday date, lastday date, versionnumber integer, description varchar(29));
create table timezone(tznumber integer primary key, difference integer not null , firstday date not null, lastday date not null);
create table station(trainchanges smallint, shortname varchar(6) primary key, layovertime integer, country varchar(4) references country, timezone integer references timezone, x integer, y integer, name varchar(29));
create table trnsattr (code varchar(4) primary key, processingcode smallint not null, description varchar(29));
create table trnsaqst(code varchar(3), inclusive boolean, question varchar(29) not null, transattr varchar(4) references trnsattr, primary key (code, transattr));
-- documentation states 'mode' instead of attr
create table trnsmode(code varchar(4) primary key, description varchar(29));
create table trnsmqst(code varchar(3), question varchar(29) not null, transmode varchar(4) references trnsmode, primary key(code, transmode));
create table connmode(code varchar(4) primary key, connectiontype smallint not null, description varchar(29));
create table contconn(fromstation varchar(6) references station, tostation varchar(6) references station, connectiontime integer not null, connectionmode varchar(4) references connmode not null, primary key(fromstation, tostation, connectionmode));
create table footnote(footnote integer, servicedate date);
create table timetable_service (serviceid integer not null, companynumber integer references company, servicenumber integer not null, variant varchar(6) not null, firststop numeric(3,0) not null, laststop numeric(3,0) not null, servicename varchar(29) not null);
create table timetable_validity (serviceid integer not null, footnote integer, firststop numeric(3,0) not null, laststop numeric(3,0) not null);
create table timetable_transport (serviceid integer not null, transmode varchar(4) references trnsmode, firststop numeric(3,0) not null, laststop numeric(3,0) not null);
create table timetable_attribute (serviceid integer not null, code varchar(4) references trnsattr, firststop numeric(3,0) not null, laststop numeric(3,0) not null);
create table timetable_stops (serviceid integer not null, station varchar(6) references station, arrivaltime time, departuretime time);
create table timetable_platform (serviceid integer not null, station varchar(6) references station, arrival varchar(4), departure varchar(4), footnote integer);
create table changes(station varchar(6) references station, fromservice integer not null, toservice integer not null, possiblechange smallint);