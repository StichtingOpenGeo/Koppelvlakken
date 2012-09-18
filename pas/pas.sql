create table stops(
	overstaphalte INT4,
        halteid VARCHAR(7) NOT NULL,
        overstaptijd DECIMAL(3),
        maxoverstaptijd DECIMAL(3),
        landcode VARCHAR(3),
        tijdzone DECIMAL(1),
        attribuut INT4,
        x DECIMAL(10) NOT NULL,
        y DECIMAL(10) NOT NULL,
        naam VARCHAR(50),
        straat VARCHAR(1),
        volgendezijstraat VARCHAR(1),
        volgendezijstraat2 VARCHAR(1),
        zone1 decimal(4),
        zone2 decimal(4),
        zone3 decimal(4),
        zone4 decimal(4),
        PRIMARY KEY (halteid)
);

copy stops from '/tmp/stops.tsv' delimiter '|' NULL as '';

create table voetnoot(
	voetnoot VARCHAR(5),
        datum DATE,
        primary key(voetnoot,datum)
);
copy voetnoot from '/tmp/voetnoot.tsv' delimiter '|' NULL as '' CSV HEADER;

create table pujo(
	modaliteit VARCHAR(1) NOT NULL,
        vervoerdercode VARCHAR(6) NOT NULL,
        lijnsysteemnr VARCHAR(4) NOT NULL,
        richting INT4 NOT NULL,
        ritnummer VARCHAR(5) NOT NULL,
        voetnoot VARCHAR(5) NOT NULL,
        PRIMARY KEY (vervoerdercode,lijnsysteemnr,ritnummer,voetnoot)
);
copy pujo from '/tmp/pujo.tsv' delimiter '|' CSV HEADER;

create table pujopass(
        vervoerdercode VARCHAR(6) NOT NULL,
        lijnsysteemnr VARCHAR(4) NOT NULL,
        richting INT4 NOT NULL,
        ritnummer VARCHAR(5) NOT NULL,
        voetnoot VARCHAR(5) NOT NULL,
        stopsequentie DECIMAL(3) NOT NULL,
        halteid VARCHAR(7) NOT NULL,
        aankomsttijd CHAR(8),
        vertrektijd CHAR(8),
        PRIMARY KEY (vervoerdercode,lijnsysteemnr,ritnummer,voetnoot,stopsequentie),
	FOREIGN KEY (halteid) REFERENCES stops(halteid) ON DELETE CASCADE
);
copy pujopass from '/tmp/pujopass.tsv' delimiter '|' CSV HEADER;
