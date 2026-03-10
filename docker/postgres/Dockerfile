FROM postgres:15

# Install pgvector
RUN apt-get update \
    && apt-get install -y postgresql-15-pgvector \
    && rm -rf /var/lib/apt/lists/*

# Copy init file
COPY db/init.sql /docker-entrypoint-initdb.d/init.sql

# Copy schema folder
COPY db/schema /db/schema