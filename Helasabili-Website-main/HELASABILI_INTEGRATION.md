# Helasabili Database Integration

This Django application retrieves land listings from the external Helasabili PostgreSQL database (Inventories table) and displays them on the website. The connection is read-only to prevent accidental modifications.

## Overview

- **Data Source:** Helasabili PostgreSQL Database - Inventories table
- **Display Field:** ProductName → Used as land listing title
- **Access Mode:** Read-only (no writes to external database)
- **Local Storage:** Imported listings stored as Course records in the main database

## Quick Start

### View Current Listings
Navigate to the Dashboard > Manage Listings to see all imported lands.

### Import Listings from Helasabili

Run the import command to sync lands from Helasabili:

```bash
python manage.py import_helasabili_lands
```

**Options:**
- `--demo` - Creates demo listings if database connection fails

**Example:**
```bash
python manage.py import_helasabili_lands --demo
```

## Model

### HelasabiliInventory (Read-Only)

Located in `helasabili/models.py`, maps to the Inventories table in the Helasabili database.

**Key Fields:**
- `id` - Inventory ID (primary key)
- `product_name` - Land title/name (from ProductName column)

The model is configured with `managed = False`, so Django won't create or modify this table.

## Database Configuration

Configured in `nchskikuyu/settings.py`:

```python
DATABASES = {
    'helasabili': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Helasabili',
        'USER': 'postgres',
        'PASSWORD': 'Chis6658',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Environment Variables

Override defaults using environment variables:

```bash
HELASABILI_DB_NAME=Helasabili
HELASABILI_DB_USER=postgres
HELASABILI_DB_PASSWORD=Chis6658
HELASABILI_DB_HOST=localhost
HELASABILI_DB_PORT=5432
```

## Database Router

The `nchskikuyu/routers.py` ensures:
- ✅ Read operations → Helasabili database
- ✅ Write operations → Blocked (prevents modifications)
- ✅ No migrations applied to external database

## Accessing Listings

### Django Dashboard
Admin Panel → Dashboard → Manage Listings (displays imported Course records)

### Django Admin
Admin Panel → Helasabili Database - External → Helasabili Inventory Items (read-only view of source data)

### Programmatically

```python
from core.models import Course

# Get all imported lands
lands = Course.objects.filter(slug__startswith='helasabili-')

# Get by title
land = Course.objects.get(title='Kahawa west')
```

## Troubleshooting

### Connection Error
If the import fails due to database connection issues:
```bash
python manage.py import_helasabili_lands --demo
```
This creates sample listings for testing.

### No Listings Appear
1. Ensure `python manage.py import_helasabili_lands` has been run
2. Check the Course records in Django admin
3. Verify the Helasabili database connection in pgAdmin

### Listings Not Updating
Run the import command periodically or set up a cron job:
```bash
0 * * * * cd /path/to/project && python manage.py import_helasabili_lands
```

## Architecture

```
Django Application
│
├── Default Database (SQLite/PostgreSQL)
│   └── Course Model
│       └── Imported land listings
│
└── Helasabili Database (Read-Only PostgreSQL)
    └── Inventories Table
        └── Product names
```

## Files

- `nchskikuyu/settings.py` - Database configuration
- `nchskikuyu/routers.py` - Database router for read-only access
- `helasabili/models.py` - HelasabiliInventory model
- `helasabili/admin.py` - Admin interface
- `core/management/commands/import_helasabili_lands.py` - Import command
