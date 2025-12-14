#!/bin/bash

sudo -u postgres psql <<EOF
CREATE DATABASE labdb;
CREATE USER labuser WITH PASSWORD 'SecurePass123!';
GRANT ALL PRIVILEGES ON DATABASE labdb TO labuser;
\c labdb
CREATE TABLE test_table (id SERIAL PRIMARY KEY, message TEXT, created_at TIMESTAMP DEFAULT NOW());
INSERT INTO test_table (message) VALUES ('Hello from Lab 2!');
INSERT INTO test_table (message) VALUES ('Multi-tier architecture works!');
\q
EOF

echo "Database setup completed successfully!"

 sudo -u postgres psql -d labdb <<EOF
  GRANT USAGE ON SCHEMA public TO labuser;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO labuser;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO labuser;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO labuser;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO labuser;
EOF

echo "Database permissions configured successfully!"