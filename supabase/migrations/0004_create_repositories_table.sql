CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id),
    url TEXT UNIQUE,
    name TEXT,
    description TEXT,
    metadata JSONB,
    crawled_at TIMESTAMPTZ DEFAULT now(),
    updated_repo_at TIMESTAMPTZ
);