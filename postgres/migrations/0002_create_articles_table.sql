CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES users(id),
    url TEXT UNIQUE,
    platform TEXT,
    title TEXT,
    content TEXT,
    metadata JSONB,
    crawled_at TIMESTAMPTZ DEFAULT now(),
    published_at TIMESTAMPTZ
);