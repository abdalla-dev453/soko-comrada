#!/bin/bash
set -e

# Generate secure secrets if not set or if using default insecure values
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "dev-secret-key-change-me" ] || [ "$SECRET_KEY" = "change-me-to-a-long-random-string" ]; then
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "dev-jwt-secret-change-me" ] || [ "$JWT_SECRET_KEY" = "change-me-to-a-different-long-random-string" ]; then
    export JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

# Use memory:// for rate limiting if Redis URL not provided (single-worker workaround)
if [ -z "$RATELIMIT_STORAGE_URI" ]; then
    export RATELIMIT_STORAGE_URI="memory://"
fi

exec "$@"
