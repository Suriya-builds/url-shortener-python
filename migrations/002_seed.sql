INSERT INTO links (code, url) VALUES
    ('welcome', 'https://docs.docker.com/get-started/'),
    ('circleci', 'https://circleci.com/docs/'),
    ('git',      'https://git-scm.com/book/en/v2')
ON CONFLICT DO NOTHING;

-- a fortnight of clicks so the stats endpoint has something to show
INSERT INTO clicks (link_id, referrer, clicked_at)
SELECT l.id,
       (ARRAY['', 'https://t.co/x', 'https://news.ycombinator.com/', 'https://google.com/'])[1 + (random()*3)::int],
       now() - (random() * interval '14 days')
FROM links l, generate_series(1, 40)
WHERE l.code <> ''
ON CONFLICT DO NOTHING;
