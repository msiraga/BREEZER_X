-- BREEZER_X Database Initialization

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Additional indexes can be added here if needed

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO breezer;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO breezer;
