CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES users(id),
    url TEXT UNIQUE,
    platform TEXT,
    content TEXT,
    metadata JSONB,
    crawled_at TIMESTAMPTZ DEFAULT now(),
    published_at TIMESTAMPTZ
);