-- Create a new SQLite3 database named 'user_quota.db' if it doesn't exist
CREATE DATABASE IF NOT EXISTS user_quota.db;

-- Connect to the 'user_quota.db' database
ATTACH DATABASE 'user_quota.db' AS user_quota;

-- Create a table to store user quota information
CREATE TABLE IF NOT EXISTS user_quota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directory TEXT NOT NULL,
    user TEXT NOT NULL,
    quota_used TEXT NOT NULL
);
