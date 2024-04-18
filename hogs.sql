DROP VIEW  IF EXISTS v_recent_hogs;
DROP VIEW  IF EXISTS v_hosts;
DROP INDEX IF EXISTS timestamp_index;
DROP TABLE IF EXISTS df_stat;
DROP TABLE IF EXISTS hosts;

CREATE TABLE hogs (
        t datetime default current_timestamp,
        host varchar(20),
        cpu_used varchar(20),
        cpu_total varchar(20),
        mem_used varchar(20),
        mem_total varchar(20)
        );

CREATE INDEX timestamp_idx on hogs(measured_at);

CREATE VIEW v_hosts as SELECT * FROM hosts ORDER BY host, partition;

CREATE VIEW v_recent_measurements as SELECT * FROM df_stat ORDER BY measured_at DESC;

