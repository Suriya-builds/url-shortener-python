CREATE TABLE IF NOT EXISTS links (
    id         SERIAL PRIMARY KEY,
    code       TEXT NOT NULL DEFAULT '',
    url        TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS links_code ON links (code) WHERE code <> '';

CREATE TABLE IF NOT EXISTS clicks (
    id         SERIAL PRIMARY KEY,
    link_id    INT NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    referrer   TEXT NOT NULL DEFAULT '',
    clicked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS clicks_link ON clicks (link_id, clicked_at DESC);
