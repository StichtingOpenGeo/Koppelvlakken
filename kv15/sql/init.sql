CREATE TABLE kv15_stopmessage (
DataOwnerCode VARCHAR(10) NOT NULL,
MessageCodeDate DATE NOT NULL,
MessageCodeNumber NUMERIC(4,0) NOT NULL,
UserStopCodes TEXT,
LinePlanningNumbers TEXT,
MessagePriority VARCHAR(10) NOT NULL,
MessageType VARCHAR(10) NOT NULL,
MessageDurationType VARCHAR(10) NOT NULL,
MessageStartTime TIMESTAMP NOT NULL,
MessageEndTime TIMESTAMP,
MessageContent VARCHAR(255),
ReasonType NUMERIC(3,0),
SubReasonType VARCHAR(10),
ReasonContent VARCHAR(255),
EffectType NUMERIC(3,0),
SubEffectType VARCHAR(10),
EffectContent VARCHAR(255),
MeasureType NUMERIC(3,0),
SubMeasureType VARCHAR(10),
MeasureContent VARCHAR(255),
AdviceType NUMERIC(3,0),
SubAdviseType VARCHAR(10),
AdviseContent VARCHAR(255),
MessageTimeStamp TIMESTAMP NOT NULL
);

CREATE TABLE kv15_deletemessage (
DataOwnerCode VARCHAR(10) NOT NULL,
MessageCodeDate DATE NOT NULL,
MessageCodeNumber NUMERIC(4,0) NOT NULL
);

CREATE TABLE kv15_current (
MessageId Serial,
DataOwnerCode VARCHAR(10) NOT NULL,
MessageCodeDate DATE NOT NULL,
MessageCodeNumber NUMERIC(4,0) NOT NULL,
UserStopCodesId BIGINT NOT NULL,
MessagePriority VARCHAR(10) NOT NULL,
MessageType VARCHAR(10) NOT NULL,
MessageDurationType VARCHAR(10) NOT NULL,
MessageStartTime TIMESTAMP NOT NULL,
MessageEndTime TIMESTAMP,
MessageContent VARCHAR(255),
ReasonType NUMERIC(3,0),
SubReasonType VARCHAR(10),
ReasonContent VARCHAR(255),
EffectType NUMERIC(3,0),
SubEffectType VARCHAR(10),
EffectContent VARCHAR(255),
MeasureType NUMERIC(3,0),
SubMeasureType VARCHAR(10),
MeasureContent VARCHAR(255),
AdviceType NUMERIC(3,0),
SubAdviseType VARCHAR(10),
AdviseContent VARCHAR(255),
MessageTimeStamp TIMESTAMP NOT NULL
);

CREATE TABLE kv15_userstop (
MessageId BIGINT NOT NULL REFERENCES kv15_current ON DELETE CASCADE,
UserStopCode VARCHAR(10) NOT NULL,
UNIQUE(MessageId, UserStopCode)
);

CREATE TABLE kv15_lineplanningnumber (
MessageId BIGINT NOT NULL REFERENCES kv15_current ON DELETE CASCADE,
LinePlanningNumber VARCHAR(10) NOT NULL,
UNIQUE(MessageId, LinePlanningNumber)
);


GRANT INSERT ON kv15_stopmessage TO kv15insert;
GRANT INSERT ON kv15_deletemessage TO kv15insert;
GRANT INSERT, UPDATE, DELETE ON kv15_current TO kv15insert;
GRANT INSERT, DELETE ON kv15_userstop TO kv15insert;
GRANT INSERT, DELETE ON kv15_lineplanningnumber TO kv15insert;
