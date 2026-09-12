-- HerkkuMarsu Database Schema
-- SQLite database for Inkubio's credits system

CREATE TABLE IF NOT EXISTS users (
    id      INTEGER PRIMARY KEY,        -- Telegram user ID (immutable)
    name    TEXT,                        -- Telegram display username
    lang    TEXT    DEFAULT 'FIN'        -- User language preference ('FIN' or 'ENG')
);

CREATE TABLE IF NOT EXISTS credits (
    user_id             INTEGER PRIMARY KEY, -- References users.id
    money               REAL    DEFAULT 0,   -- Current credit balance
    latest_change       TEXT,                -- Description of last action (e.g. 'add money', 'use money')
    latest_change_time  TEXT,                -- Timestamp of last action (ISO format)
    FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);
