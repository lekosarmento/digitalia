-- Enable standard PostgreSQL extensions required for primary keys (UUID) and secure hashing/encryption
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
