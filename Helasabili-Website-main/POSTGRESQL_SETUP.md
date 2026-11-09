# PostgreSQL Setup Guide for NCHSM Kikuyu Campus

## Database Configuration

Your PostgreSQL configuration:
- **Host**: localhost
- **Port**: 5432
- **Database**: School_DB
- **Username**: postgres
- **Password**: Chris6658

## Prerequisites

1. PostgreSQL installed (version 12+)
2. PostgreSQL service running
3. Database `School_DB` created
4. User `postgres` configured

## Setup Steps

### 1. Verify PostgreSQL Installation

```bash
# Windows (CMD/PowerShell)
psql --version

# Linux/Mac
psql --version
```

### 2. Connect to PostgreSQL

```bash
# Windows
psql -U postgres

# Linux/Mac
sudo -u postgres psql
```

### 3. Create Database (if not exists)

```sql
CREATE DATABASE School_DB;
```

### 4. Create User (if not exists)

```sql
CREATE USER postgres WITH PASSWORD 'Chris6658';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET default_transaction_deferrable TO on;
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE School_DB TO postgres;
```

### 5. Verify Connection

```bash
# Test the connection
psql -U postgres -d School_DB -h localhost -p 5432
```

## Django Configuration

The `.env` file is already configured with:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=School_DB
DB_USER=postgres
DB_PASSWORD=Chris6658
DB_HOST=localhost
DB_PORT=5432
```

## Installation

### 1. Install PostgreSQL Driver

```bash
pip install psycopg2-binary==2.9.9
```

### 2. Update Requirements

Already done - `requirements.txt` includes psycopg2-binary

### 3. Install All Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Server

```bash
python manage.py runserver
```

## Troubleshooting

### Connection Error: "password authentication failed"
- Verify password: `Chris6658`
- Check PostgreSQL service is running
- Ensure user `postgres` exists

### Connection Error: "database does not exist"
- Create database: `CREATE DATABASE School_DB;`
- Verify name matches `.env` file

### Connection Error: "could not connect to server"
- Check PostgreSQL is running
- Verify host: `localhost`
- Verify port: `5432`
- Check firewall settings

### psycopg2 installation fails
```bash
# Try binary version
pip install psycopg2-binary

# Or source version (requires build tools)
pip install psycopg2
```

## Database Backup

### Backup Database

```bash
# Windows
pg_dump -U postgres -d School_DB > backup.sql

# Linux/Mac
pg_dump -U postgres -d School_DB > backup.sql
```

### Restore Database

```bash
# Windows
psql -U postgres -d School_DB < backup.sql

# Linux/Mac
psql -U postgres -d School_DB < backup.sql
```

## Useful PostgreSQL Commands

```sql
-- List all databases
\l

-- Connect to database
\c School_DB

-- List all tables
\dt

-- List all users
\du

-- Show database size
SELECT pg_size_pretty(pg_database_size('School_DB'));

-- Show table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables WHERE schemaname != 'pg_catalog'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Backup to SQL file
pg_dump -U postgres -d School_DB > backup_$(date +%Y%m%d_%H%M%S).sql

-- Show active connections
SELECT pid, usename, application_name, state FROM pg_stat_activity WHERE datname = 'School_DB';

-- Kill idle connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE datname = 'School_DB' AND state = 'idle' AND query_start < NOW() - INTERVAL '10 minutes';
```

## Performance Tips

1. **Enable Connection Pooling**: Use PgBouncer or django-db-gevent
2. **Add Indexes**: For frequently queried fields
3. **Optimize Queries**: Use select_related() and prefetch_related()
4. **Monitor Performance**: Use pg_stat_statements
5. **Regular Backups**: Set up automated backups
6. **Vacuum Regularly**: Remove dead tuples

## Production Considerations

### Before Going Live

- [ ] Change password from default
- [ ] Enable SSL connections
- [ ] Set up regular backups
- [ ] Configure user permissions
- [ ] Monitor performance
- [ ] Set up logging
- [ ] Configure maintenance windows
- [ ] Test disaster recovery

### Production Connection String

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=School_DB
DB_USER=app_user
DB_PASSWORD=strong-password-here
DB_HOST=prod-db.example.com
DB_PORT=5432
```

### Create Production User

```sql
CREATE USER app_user WITH PASSWORD 'strong-password-here';
GRANT CONNECT ON DATABASE School_DB TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
```

## Testing Connection

```python
# In Django shell
python manage.py shell

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
```

## Additional Resources

- PostgreSQL Docs: https://www.postgresql.org/docs/
- psycopg2 Docs: https://www.psycopg.org/
- Django Database: https://docs.djangoproject.com/en/4.2/ref/settings/#databases
- PgAdmin: https://www.pgadmin.org/

---

**Note**: Your current credentials are configured in the `.env` file. Never commit this file to version control!
