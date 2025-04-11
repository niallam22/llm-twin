CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_user_id TEXT UNIQUE,
    username TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);