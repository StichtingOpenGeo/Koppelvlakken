CREATE TABLE kv6(
MessageType VARCHAR(10) NOT NULL,
DataOwnerCode VARCHAR(10) NOT NULL,
LinePlanningNumber VARCHAR(10) NOT NULL,
OperatingDay DATE NOT NULL,
JourneyNumber NUMERIC(6,0) NOT NULL,
ReinforcementNumber NUMERIC(2,0) NOT NULL,
UserStopCode VARCHAR(10),
PassageSequenceNumber NUMERIC(4,0),
Timestamp TIMESTAMP NOT NULL,
Source VARCHAR(10) NOT NULL,
VehicleNumber NUMERIC(6,0),
Punctuality NUMERIC(4,0),
BlockCode NUMERIC(8,0),
WheelChairAccessible BOOLEAN,
NumberOfCoaches NUMERIC(2,0),
DistanceSinceLastUserStop NUMERIC(5,0),
RD_X NUMERIC(6,0),
RD_Y NUMERIC(6,0)
);
grant insert, update on kv6 to kv6insert;

CREATE TABLE kv6_current(
MessageType VARCHAR(10) NOT NULL,
DataOwnerCode VARCHAR(10) NOT NULL,
LinePlanningNumber VARCHAR(10) NOT NULL,
OperatingDay DATE NOT NULL,
JourneyNumber NUMERIC(6,0) NOT NULL,
ReinforcementNumber NUMERIC(2,0) NOT NULL,
UserStopCode VARCHAR(10),
PassageSequenceNumber NUMERIC(4,0),
Timestamp TIMESTAMP NOT NULL,
Source VARCHAR(10) NOT NULL,
VehicleNumber NUMERIC(6,0),
Punctuality NUMERIC(4,0),
BlockCode NUMERIC(8,0),
WheelChairAccessible BOOLEAN,
NumberOfCoaches NUMERIC(2,0),
DistanceSinceLastUserStop NUMERIC(5,0),
RD_X NUMERIC(6,0),
RD_Y NUMERIC(6,0),
Terminated BOOLEAN
);
grant insert, update, delete on kv6_current to kv6insert;
