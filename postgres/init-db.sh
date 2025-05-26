#!/bin/bash
set -e

echo "Starting database initialization..."

# Apply migrations in order
MIGRATION_DIR="/docker-entrypoint-initdb.d/migrations"

if [ -d "$MIGRATION_DIR" ]; then
    echo "Applying migrations from $MIGRATION_DIR"
    
    # Sort files numerically and apply them
    for migration_file in $(ls "$MIGRATION_DIR"/*.sql 2>/dev/null | sort -V); do
        if [ -f "$migration_file" ]; then
            echo "Applying migration: $(basename "$migration_file")"
            psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$migration_file"
        fi
    done
    
    echo "All migrations applied successfully!"
else
    echo "Warning: Migration directory $MIGRATION_DIR not found"
fi

echo "Database initialization complete!"