-- Create table for hog reports
CREATE TABLE IF NOT EXISTS hog_reports (
    id INTEGER PRIMARY KEY,
    server TEXT,
    directory TEXT,
    user TEXT,
    quota_used REAL
);
