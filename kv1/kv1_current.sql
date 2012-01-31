CREATE TABLE "sys"."kv1_current" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "lineplanningnumber"    VARCHAR(10)   NOT NULL,
        "operatingday"          DATE          NOT NULL,
        "journeynumber"         DECIMAL(6)    NOT NULL,
        "journeypatterncode"    VARCHAR(10)   NOT NULL,
        "userstopcode"          VARCHAR(10)   NOT NULL,
        "passagesequencenumber" DECIMAL(4)    NOT NULL,
        "passtime"              TIMESTAMP     NOT NULL
);

grant select on pujo to kv1_dot;
grant select on timdemrnt to kv1_dot;
grant select on usrstop to kv1_dot;
grant select on pegrval to kv1_dot;
grant insert on kv1_current to kv1_dot;
