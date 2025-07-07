CREATE TABLE annual_reports_download_links (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    company_name TEXT NOT NULL,
    from_year INTEGER,
    to_year INTEGER,
    submission_type TEXT,
    broadcast_dttm TIMESTAMP NULL,
    dissemination_dttm TIMESTAMP NULL,
    time_taken INTERVAL NULL,
    file_url TEXT NOT NULL,
    source_url TEXT NOT NULL,
    local_save_path TEXT NULL,
    is_downloaded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
