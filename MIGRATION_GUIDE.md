# Django Migration Setup Guide

## Prerequisites Check

Before running migrations, ensure you have:

✓ Django installed: `pip install Django==4.2.7`
✓ PostgreSQL driver: `pip install psycopg2-binary==2.9.9`
✓ Python 3.8+
✓ PostgreSQL running on localhost:5432
✓ Database `School_DB` created
✓ `.env` file configured with PostgreSQL credentials

## Pre-Migration Checklist

- [x] Python environment activated
- [x] requirements.txt installed
- [x] .env file configured
- [x] PostgreSQL running
- [x] Database exists
- [x] Django apps configured in settings.py

## Step 1: Verify Django Installation

```bash
# Check Django version
python -m django --version
# Output should be: 4.2.7
```

## Step 2: Verify Database Connection

```bash
# Connect to PostgreSQL and verify database
psql -U postgres -d School_DB -h localhost -p 5432

# In PostgreSQL prompt, verify you're connected:
\c School_DB
\q
```

## Step 3: Create Migrations

Run this command to create initial migrations for all apps:

```bash
python manage.py makemigrations
```

**Expected Output:**
```
Migrations for 'core':
  core/migrations/0001_initial.py
    - Create model Course
    - Create model BlogPost
    - Create model Testimonial
    - Create model GalleryImage
    - Create model Application
    - Create model AboutPage
    - Create model ContactInfo
    - Create model AdminProfile
Migrations for 'website':
  website/migrations/0001_initial.py
Migrations for 'dashboard':
  dashboard/migrations/0001_initial.py
```

## Step 4: Review Migrations

Check the generated migration files:

```bash
# View core app migrations
cat core/migrations/0001_initial.py

# View website app migrations
cat website/migrations/0001_initial.py

# View dashboard app migrations
cat dashboard/migrations/0001_initial.py
```

## Step 5: Apply Migrations

Run migrations to create all database tables:

```bash
python manage.py migrate
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, core, website, dashboard
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_user_max_length... OK
  ...
  Applying core.0001_initial... OK
  Applying website.0001_initial... OK
  Applying dashboard.0001_initial... OK
```

## Step 6: Verify Database Tables

Check if tables were created:

```bash
# Connect to database
psql -U postgres -d School_DB -h localhost -p 5432

# List all tables
\dt

# You should see:
# Schema |                    Name                    | Type  | Owner
# --------+--------------------------------------------+-------+----------
#  public | auth_group                                 | table | postgres
#  public | auth_group_permissions                     | table | postgres
#  public | auth_permission                            | table | postgres
#  public | auth_user                                  | table | postgres
#  public | auth_user_groups                           | table | postgres
#  public | auth_user_user_permissions                 | table | postgres
#  public | core_aboutpage                             | table | postgres
#  public | core_adminprofile                          | table | postgres
#  public | core_application                           | table | postgres
#  public | core_blogpost                              | table | postgres
#  public | core_course                                | table | postgres
#  public | core_galleryimage                          | table | postgres
#  public | core_testimonial                           | table | postgres
#  public | core_contactinfo                           | table | postgres
#  public | django_admin_log                           | table | postgres
#  public | django_content_type                        | table | postgres
#  public | django_migrations                          | table | postgres
#  public | django_session                             | table | postgres

\q
```

## Step 7: Create Superuser (Admin)

After migrations are complete, create an admin user:

```bash
python manage.py createsuperuser
```

**Interactive Prompts:**
```
Username: admin
Email: admin@nchskikuyu.ac.ke
Password: (enter your password)
Password (again): (confirm password)
Superuser created successfully.
```

## Step 8: Load Demo Data (Optional)

Load sample data into the database:

```bash
python manage.py shell < load_demo_data.py
```

**Expected Output:**
```
Loading demo data...
✓ Contact information created
✓ About page created
✓ Course created: Diploma in Nursing
✓ Course created: Diploma in Clinical Medicine
✓ Course created: Certificate in Health Information Management
✓ Course created: Diploma in Business Management
✓ Blog post created: Welcome to NCHSM Kikuyu Campus
✓ Blog post created: New Intakes for 2024
✓ Blog post created: Our Commitment to Quality Education
✓ Testimonial created: Grace Kipchoge
✓ Testimonial created: Peter Karanja
✓ Testimonial created: Elizabeth Muriuki
✓ Gallery image created: Main Classroom Block
✓ Gallery image created: Clinical Laboratory
✓ Gallery image created: Campus View
✓ Gallery image created: Graduation Ceremony

✓ Demo data loading completed successfully!
```

## Step 9: Collect Static Files

Prepare static files for the website:

```bash
python manage.py collectstatic --noinput
```

**Expected Output:**
```
131 static files copied to '/path/to/nchskikuyu/staticfiles', 0 unmodified, 0 post-processed.
```

## Step 10: Start Development Server

Start the Django development server:

```bash
python manage.py runserver
```

**Expected Output:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
[DATE TIME] Starting development server at http://127.0.0.1:8000/
[DATE TIME] Quit the server with CONTROL-C.
```

## Access the Application

- **Website**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/dashboard/login/
- **Django Admin**: http://localhost:8000/admin/

Login credentials:
- **Username**: admin
- **Password**: (your chosen password)

## Troubleshooting

### Error: "database does not exist"
```bash
# Create the database
psql -U postgres -c "CREATE DATABASE School_DB;"
```

### Error: "password authentication failed"
```
Check your .env file has correct credentials:
DB_USER=postgres
DB_PASSWORD=Chris6658
```

### Error: "psycopg2 not installed"
```bash
pip install psycopg2-binary==2.9.9
```

### Error: "connection refused"
```
Ensure PostgreSQL is running:
Windows: Check Services or run: pg_ctl -D "C:\Program Files\PostgreSQL\data" start
Linux: sudo systemctl start postgresql
Mac: brew services start postgresql
```

### Error: "relation does not exist"
Run migrations again:
```bash
python manage.py migrate
```

### Error: "no such table: django_session"
```bash
python manage.py migrate sessions
```

## Useful Migration Commands

```bash
# Show migration status
python manage.py showmigrations

# Show specific app migrations
python manage.py showmigrations core

# Revert last migration (be careful!)
python manage.py migrate core 0001

# Create empty migration
python manage.py makemigrations --empty core --name my_migration

# Dry-run migrations (preview without applying)
python manage.py migrate --plan

# Show SQL for migrations
python manage.py sqlmigrate core 0001
```

## Next Steps After Migration

1. ✓ Access admin panel: http://localhost:8000/admin/
2. ✓ Add course information in dashboard
3. ✓ Upload course images
4. ✓ Create blog posts
5. ✓ Upload testimonials
6. ✓ Configure contact information
7. ✓ Test application form
8. ✓ View submitted applications

## Backup Database

```bash
# Backup after successful migration
pg_dump -U postgres -d School_DB > backup_initial_$(date +%Y%m%d_%H%M%S).sql
```

## Database Size

Check database size after migration:

```bash
psql -U postgres -d School_DB -c "SELECT pg_size_pretty(pg_database_size('School_DB'));"
```

Expected output: `~5-10 MB` (will grow with data)

---

**Status**: Ready for Migration
**Database**: PostgreSQL on localhost:5432
**Database Name**: School_DB
**User**: postgres
