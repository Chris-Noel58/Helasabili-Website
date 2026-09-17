<<<<<<< HEAD
# NCHSM Kikuyu Campus - Professional Website System

A comprehensive Django-based website system for Nakuru College of Health Sciences and Management - Kikuyu Campus with a powerful admin dashboard.

## Project Overview

This is a full-featured, production-ready website system built with:
- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: PostgreSQL/MySQL (supports SQLite for development)
- **Authentication**: Django built-in authentication system
- **Admin Panel**: Custom dashboard with multiple management sections

## Features

### Public Website
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Home page with hero section
- ✅ About page with college information
- ✅ Dynamic courses listing and detail pages
- ✅ Blog/News system
- ✅ Gallery with lightbox effect
- ✅ Student testimonials
- ✅ Application form with database storage
- ✅ Contact page with Google Maps integration
- ✅ Newsletter subscription
- ✅ SEO-friendly structure
- ✅ Smooth animations and transitions

### Admin Dashboard
- ✅ Custom login system
- ✅ Dashboard home with statistics
- ✅ Course management (CRUD)
- ✅ Blog post management
- ✅ Testimonial management
- ✅ Gallery image management with categorization
- ✅ Application viewer with filtering and export
- ✅ About page editor
- ✅ Contact information manager
- ✅ Role-based access control
- ✅ Real-time statistics

## Installation

### 1. Prerequisites
- Python 3.8+
- Git
- virtualenv (recommended)
- PostgreSQL or MySQL (optional, SQLite for development)

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd nchskikuyu

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# For SQLite (default, development only):
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# For PostgreSQL:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=nchskikuyu
# DB_USER=postgres
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=5432

# For MySQL:
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=nchskikuyu
# DB_USER=root
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=3306

# Email Configuration (for contact forms)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security (set to True in production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations (creates all tables)
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow prompts to create admin credentials
```

### 5. Create Directory Structure

```bash
# Create necessary directories
mkdir -p media/courses
mkdir -p media/blog
mkdir -p media/gallery
mkdir -p media/testimonials
mkdir -p media/admin
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p logs
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Running the Server

### Development Server

```bash
python manage.py runserver
```

Access the website at `http://localhost:8000`

Access the dashboard at `http://localhost:8000/dashboard/login/`

Access Django admin at `http://localhost:8000/admin/`

### Production Deployment

For production, use:

```bash
# Using Gunicorn
gunicorn nchskikuyu.wsgi:application --bind 0.0.0.0:8000

# Using uWSGI
uwsgi --http :8000 --wsgi-file nchskikuyu/wsgi.py --master --processes 4 --threads 2
```

## Project Structure

```
nchskikuyu/
├── nchskikuyu/              # Main project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI application
│   └── __init__.py
├── core/                    # Core app (models, forms, context processors)
│   ├── models.py            # Database models
│   ├── forms.py             # Django forms
│   ├── admin.py             # Django admin customization
│   ├── context_processors.py # Template context
│   ├── apps.py
│   └── migrations/
├── website/                 # Public website app
│   ├── views.py             # Website views
│   ├── urls.py              # Website routing
│   ├── apps.py
│   └── migrations/
├── dashboard/               # Admin dashboard app
│   ├── views.py             # Dashboard views
│   ├── urls.py              # Dashboard routing
│   ├── apps.py
│   └── migrations/
├── templates/
│   ├── base.html            # Base template
│   ├── partials/            # Reusable template components
│   │   ├── navbar.html
│   │   └── footer.html
│   ├── website/             # Public website templates
│   │   ├── index.html
│   │   ├── about.html
│   │   ├── courses.html
│   │   ├── blog.html
│   │   └── ...
│   └── dashboard/           # Admin dashboard templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       └── ...
├── static/
│   ├── css/
│   │   └── style.css        # Main stylesheet
│   ├── js/
│   │   └── main.js          # Main JavaScript
│   └── images/              # Static images
├── media/                   # User uploaded files
│   ├── courses/
│   ├── blog/
│   ├── gallery/
│   ├── testimonials/
│   └── admin/
├── logs/                    # Application logs
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables

```

## Database Models

### Core Models
1. **Course** - Course programs
2. **BlogPost** - News and blog articles
3. **Testimonial** - Student testimonials
4. **GalleryImage** - Campus gallery images
5. **Application** - Student applications
6. **AboutPage** - About page content
7. **ContactInfo** - Contact information
8. **AdminProfile** - Admin user profiles

## Admin Dashboard Features

### Dashboard Home
- Total applications count
- Total courses count
- Total blog posts count
- Total gallery images
- Recent applications list
- Quick action buttons

### Content Management

#### Courses
- Add/Edit/Delete courses
- Set intake periods
- Configure fees
- Upload featured images
- Set display order
- Activate/Deactivate courses

#### Blog Posts
- Create/Edit/Delete posts
- Set publish status (Draft/Published/Archived)
- Upload featured images
- Track views
- Mark as featured

#### Testimonials
- Add/Edit/Delete testimonials
- Upload student photos
- Star rating system
- Order management

#### Gallery
- Upload images with categories
- Filter by category (Classroom, Event, Graduation, Lab, Campus Life)
- Add descriptions
- Manage display order

#### Applications
- View all student applications
- Filter by status (New/Reviewed/Accepted/Rejected/Pending)
- Search by name, email, phone
- Update application status
- Export to CSV

#### About Page
- Edit college history
- Update mission statement
- Modify vision
- Update values
- Add principal's message with photo
- Campus description and location

#### Contact Information
- Phone numbers (primary & secondary)
- Email addresses
- Physical address
- Social media links
- Google Maps coordinates
- Operating hours

## API Endpoints

### Public Website Routes
- `/` - Home page
- `/about/` - About page
- `/courses/` - Courses list
- `/course/<slug>/` - Course detail
- `/blog/` - Blog list
- `/blog/<slug>/` - Blog post detail
- `/gallery/` - Gallery
- `/testimonials/` - Testimonials
- `/apply/` - Application form
- `/contact/` - Contact page

### Dashboard Routes
- `/dashboard/login/` - Admin login
- `/dashboard/` - Dashboard home
- `/dashboard/courses/` - Manage courses
- `/dashboard/blog/` - Manage blog posts
- `/dashboard/testimonials/` - Manage testimonials
- `/dashboard/gallery/` - Manage gallery
- `/dashboard/applications/` - View applications
- `/dashboard/about/edit/` - Edit about page
- `/dashboard/contact/edit/` - Edit contact info
- `/dashboard/logout/` - Logout

## Security Features

- ✅ CSRF protection
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection
- ✅ Admin authentication required
- ✅ Password hashing
- ✅ Environment variables for sensitive data
- ✅ SSL/TLS support

## Performance Optimization

- ✅ Image optimization on upload
- ✅ Database query optimization with select_related/prefetch_related
- ✅ Caching support
- ✅ Static file compression (WhiteNoise)
- ✅ CDN-ready structure

## Customization

### Changing Colors

Edit `/static/css/style.css` and modify CSS variables:

```css
:root {
    --primary: #6366f1;
    --secondary: #764ba2;
    --success: #10b981;
    /* ... */
}
```

### Adding New Pages

1. Create a view in `website/views.py`
2. Add URL in `website/urls.py`
3. Create template in `templates/website/`
4. Add navigation link in `templates/partials/navbar.html`

### Adding New Admin Features

1. Create model in `core/models.py`
2. Create form in `core/forms.py`
3. Create views in `dashboard/views.py`
4. Add URLs in `dashboard/urls.py`
5. Create templates in `templates/dashboard/`

## Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database Migration Issues
```bash
python manage.py migrate --run-syncdb
python manage.py migrate core
python manage.py migrate website
python manage.py migrate dashboard
```

### Create Fresh Database
```bash
# Backup existing data first
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Permission Denied on Linux
```bash
chmod +x manage.py
chmod -R 755 media/
```

## Deployment Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG = False
- [ ] Configure allowed hosts
- [ ] Set up production database
- [ ] Configure email settings
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Create admin superuser
- [ ] Upload initial content
- [ ] Test all forms and features
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Test error pages (404, 500)

## Support & Documentation

For Django documentation, visit: https://docs.djangoproject.com/
For Bootstrap documentation, visit: https://getbootstrap.com/docs/

## License

This project is proprietary software for Nakuru College of Health Sciences and Management.

## Contact

For technical support, contact the IT department at NCHSM Kikuyu Campus.

## Changelog

### Version 1.0.0 (2024)
- Initial release
- Core functionality implemented
- Admin dashboard complete
- Responsive design
- All required features
=======
# KIKUYU-CAMPUS-WEBSITE
>>>>>>> 450a5d7bcdc78f33adb28025e7c05919c2d628ea
