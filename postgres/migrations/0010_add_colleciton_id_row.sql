DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'articles' 
        AND column_name = 'collection_id'
    ) THEN
        ALTER TABLE articles ADD COLUMN collection_id TEXT;
        RAISE NOTICE 'Added collection_id column to articles table';
    ELSE
        RAISE NOTICE 'collection_id column already exists';
    END IF;
END $$;