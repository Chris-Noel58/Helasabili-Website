# Directory Structure Documentation

## Complete File Tree

```
nchskikuyu/                              # Root project directory
│
├── nchskikuyu/                          # Main Django project package
│   ├── __init__.py                      # Package initialization
│   ├── settings.py                      # Django configuration
│   ├── urls.py                          # Main URL routing
│   ├── wsgi.py                          # WSGI application
│   └── asgi.py                          # ASGI application (if async)
│
├── core/                                # Core application
│   ├── __init__.py                      # Package initialization
│   ├── models.py                        # Database models (8 models)
│   ├── forms.py                         # Django forms
│   ├── admin.py                         # Django admin customization
│   ├── apps.py                          # App configuration
│   ├── context_processors.py            # Template context functions
│   ├── tests.py                         # Unit tests
│   ├── views.py                         # Helper views (if needed)
│   ├── managers.py                      # Custom model managers
│   ├── signals.py                       # Django signals
│   ├── utils.py                         # Utility functions
│   ├── validators.py                    # Field validators
│   └── migrations/                      # Database migrations
│       ├── __init__.py
│       ├── 0001_initial.py
│       └── ...
│
├── website/                             # Public website application
│   ├── __init__.py                      # Package initialization
│   ├── views.py                         # View handlers (10+ views)
│   │   ├── home()
│   │   ├── about()
│   │   ├── courses()
│   │   ├── course_detail()
│   │   ├── blog_list()
│   │   ├── blog_detail()
│   │   ├── gallery()
│   │   ├── testimonials()
│   │   ├── apply()
│   │   ├── contact()
│   │   └── ...
│   ├── urls.py                          # Website URL routing
│   ├── apps.py                          # App configuration
│   ├── tests.py                         # Unit tests
│   ├── migrations/                      # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── templatetags/                    # Custom template tags
│       ├── __init__.py
│       └── custom_tags.py
│
├── dashboard/                           # Admin dashboard application
│   ├── __init__.py                      # Package initialization
│   ├── views.py                         # Dashboard views (30+ views)
│   │   ├── DashboardHomeView
│   │   ├── CourseListView
│   │   ├── CourseCreateView
│   │   ├── CourseUpdateView
│   │   ├── CourseDeleteView
│   │   ├── BlogListView
│   │   ├── BlogCreateView
│   │   ├── BlogUpdateView
│   │   ├── BlogDeleteView
│   │   ├── ApplicationListView
│   │   ├── ApplicationDetailView
│   │   ├── GalleryListView
│   │   ├── GalleryUploadView
│   │   ├── GalleryUpdateView
│   │   ├── GalleryDeleteView
│   │   ├── TestimonialListView
│   │   ├── TestimonialCreateView
│   │   ├── TestimonialUpdateView
│   │   ├── TestimonialDeleteView
│   │   ├── AboutEditView
│   │   ├── ContactEditView
│   │   ├── ExportApplicationsCSV
│   │   └── ...
│   ├── urls.py                          # Dashboard URL routing
│   ├── apps.py                          # App configuration
│   ├── decorators.py                    # Custom decorators
│   ├── tests.py                         # Unit tests
│   ├── middleware.py                    # Custom middleware
│   ├── migrations/                      # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── utils.py                         # Dashboard utilities
│
├── templates/                           # HTML templates
│   ├── base.html                        # Base template (extends all pages)
│   ├── index.html                       # Root template if needed
│   │
│   ├── partials/                        # Reusable components
│   │   ├── navbar.html                  # Navigation bar
│   │   ├── footer.html                  # Footer
│   │   ├── breadcrumbs.html             # Breadcrumbs
│   │   ├── pagination.html              # Pagination
│   │   └── messages.html                # Django messages
│   │
│   ├── website/                         # Public website templates
│   │   ├── index.html                   # Home page
│   │   ├── about.html                   # About page
│   │   ├── apply.html                   # Application form
│   │   ├── contact.html                 # Contact page
│   │   ├── courses.html                 # Courses list
│   │   ├── course_detail.html           # Course detail
│   │   ├── blog.html                    # Blog list
│   │   ├── blog_detail.html             # Blog post detail
│   │   ├── gallery.html                 # Gallery
│   │   ├── testimonials.html            # Testimonials
│   │   └── newsletter.html              # Newsletter signup
│   │
│   ├── dashboard/                       # Dashboard templates
│   │   ├── base.html                    # Dashboard base
│   │   ├── login.html                   # Login page
│   │   ├── index.html                   # Dashboard home
│   │   │
│   │   ├── courses/                     # Course management
│   │   │   ├── list.html                # Courses list
│   │   │   └── form.html                # Course form (create/edit)
│   │   │
│   │   ├── blog/                        # Blog management
│   │   │   ├── list.html                # Blog posts list
│   │   │   └── form.html                # Blog form (create/edit)
│   │   │
│   │   ├── gallery/                     # Gallery management
│   │   │   ├── list.html                # Gallery list
│   │   │   └── form.html                # Gallery form
│   │   │
│   │   ├── testimonials/                # Testimonials management
│   │   │   ├── list.html                # Testimonials list
│   │   │   └── form.html                # Testimonial form
│   │   │
│   │   ├── applications/                # Applications management
│   │   │   ├── list.html                # Applications list
│   │   │   └── detail.html              # Application detail
│   │   │
│   │   ├── about/                       # About page management
│   │   │   └── form.html                # About form
│   │   │
│   │   └── contact/                     # Contact info management
│   │       └── form.html                # Contact form
│   │
│   └── errors/                          # Error pages
│       ├── 404.html                     # Page not found
│       └── 500.html                     # Server error
│
├── static/                              # Static files (CSS, JS, images)
│   ├── css/                             # Stylesheets
│   │   ├── style.css                    # Main stylesheet
│   │   ├── bootstrap.css                # Bootstrap (if custom)
│   │   ├── responsive.css               # Responsive styles
│   │   └── animations.css               # Animation styles
│   │
│   ├── js/                              # JavaScript files
│   │   ├── main.js                      # Main JavaScript
│   │   ├── bootstrap.js                 # Bootstrap JS
│   │   ├── forms.js                     # Form utilities
│   │   ├── api.js                       # API helpers
│   │   └── utils.js                     # Utility functions
│   │
│   ├── images/                          # Static images
│   │   ├── logo.png                     # Logo
│   │   ├── favicon.ico                  # Favicon
│   │   ├── hero.jpg                     # Hero image
│   │   ├── background.jpg               # Background
│   │   └── icons/                       # Icon set
│   │
│   ├── fonts/                           # Custom fonts
│   │   ├── roboto.woff2
│   │   └── opensans.woff2
│   │
│   └── lib/                             # JavaScript libraries
│       ├── bootstrap.min.js
│       ├── jquery.min.js
│       ├── lightbox.js
│       └── ...
│
├── media/                               # User uploaded files
│   ├── courses/                         # Course images
│   │   ├── course-1-featured.jpg
│   │   ├── course-2-featured.jpg
│   │   └── ...
│   │
│   ├── blog/                            # Blog images
│   │   ├── post-1-featured.jpg
│   │   ├── post-2-featured.jpg
│   │   └── ...
│   │
│   ├── gallery/                         # Gallery images
│   │   ├── classroom-1.jpg
│   │   ├── event-1.jpg
│   │   ├── graduation-1.jpg
│   │   ├── lab-1.jpg
│   │   └── ...
│   │
│   ├── testimonials/                    # Student photos
│   │   ├── student-1.jpg
│   │   ├── student-2.jpg
│   │   └── ...
│   │
│   └── admin/                           # Admin uploads
│       ├── profile-1.jpg
│       ├── principal-photo.jpg
│       └── ...
│
├── logs/                                # Application logs
│   ├── django.log                       # Django logs
│   ├── error.log                        # Error logs
│   ├── access.log                       # Access logs
│   └── ...
│
├── staticfiles/                         # Collected static files (production)
│   ├── admin/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── ...
│
├── manage.py                            # Django management script
├── requirements.txt                     # Python dependencies
├── .env                                 # Environment variables (local)
├── .env.example                         # Environment template
├── .gitignore                           # Git ignore rules
│
├── README.md                            # Main documentation
├── QUICKSTART.md                        # Quick start guide
├── DEPLOYMENT.md                        # Deployment guide
├── API_DOCUMENTATION.md                 # API reference
├── PROJECT_SUMMARY.md                   # Project overview
├── FEATURE_CHECKLIST.md                 # Feature status
│
├── install.sh                           # Linux/Mac installer
├── install.bat                          # Windows installer
├── load_demo_data.py                    # Demo data loader
│
└── .git/                                # Git repository (if initialized)
    ├── config
    ├── objects/
    ├── refs/
    └── ...
```

## File Descriptions

### Root Level Files

| File | Purpose |
|------|---------|
| `manage.py` | Django command-line utility |
| `requirements.txt` | Python package dependencies |
| `.env` | Environment variables (local) |
| `.env.example` | Environment template |
| `.gitignore` | Git ignore rules |
| `README.md` | Main documentation |
| `QUICKSTART.md` | Quick setup guide |
| `DEPLOYMENT.md` | Deployment instructions |
| `API_DOCUMENTATION.md` | API reference |
| `PROJECT_SUMMARY.md` | Project overview |
| `FEATURE_CHECKLIST.md` | Features status |
| `install.sh` | Linux/Mac installer |
| `install.bat` | Windows installer |
| `load_demo_data.py` | Demo data script |

### Django Project (nchskikuyu/)

| File | Purpose |
|------|---------|
| `settings.py` | Django configuration |
| `urls.py` | Main URL routing |
| `wsgi.py` | WSGI application |
| `asgi.py` | ASGI application |

### Core App (core/)

| File | Purpose |
|------|---------|
| `models.py` | Database model definitions |
| `forms.py` | Django form definitions |
| `admin.py` | Django admin customization |
| `apps.py` | App configuration |
| `context_processors.py` | Template context functions |

### Website App (website/)

| File | Purpose |
|------|---------|
| `views.py` | Public website view handlers |
| `urls.py` | Website URL patterns |
| `apps.py` | App configuration |

### Dashboard App (dashboard/)

| File | Purpose |
|------|---------|
| `views.py` | Dashboard view handlers |
| `urls.py` | Dashboard URL patterns |
| `apps.py` | App configuration |
| `decorators.py` | Custom decorators |

### Templates (templates/)

| Directory | Purpose |
|-----------|---------|
| `base.html` | Base template for all pages |
| `partials/` | Reusable components |
| `website/` | Public website templates |
| `dashboard/` | Dashboard templates |
| `errors/` | Error page templates |

### Static Files (static/)

| Directory | Purpose |
|-----------|---------|
| `css/` | Stylesheets |
| `js/` | JavaScript files |
| `images/` | Static images |
| `fonts/` | Custom fonts |
| `lib/` | Third-party libraries |

### Media Files (media/)

| Directory | Purpose |
|-----------|---------|
| `courses/` | Course featured images |
| `blog/` | Blog post images |
| `gallery/` | Gallery images by category |
| `testimonials/` | Student photos |
| `admin/` | Admin uploads |

## Directory Size Guidelines

- `static/` - ~50-100 MB (with libraries)
- `media/` - Grows with uploads (typically 500 MB - 2 GB)
- `templates/` - ~5-10 MB
- `logs/` - Grows with usage (typically 10-50 MB)
- `venv/` - ~300-500 MB (not in repository)

## File Naming Conventions

### Python Files
- `models.py` - Database models
- `views.py` - View handlers
- `forms.py` - Form definitions
- `urls.py` - URL patterns
- `admin.py` - Admin customization
- `apps.py` - App configuration
- `managers.py` - Custom managers
- `signals.py` - Django signals
- `utils.py` - Utility functions
- `validators.py` - Field validators
- `decorators.py` - Custom decorators

### HTML Templates
- Use snake_case: `course_detail.html`
- Use descriptive names: `blog_post_form.html`
- Use directory structure for organization

### CSS Files
- `style.css` - Main styles
- `responsive.css` - Responsive design
- `animations.css` - Animations
- Library files: `bootstrap.css`

### JavaScript Files
- `main.js` - Main script
- `utils.js` - Utility functions
- `api.js` - API helpers
- `forms.js` - Form handling
- Library files: `bootstrap.js`, `jquery.js`

### Media Files
- Images: `.jpg`, `.png`, `.gif`
- Use descriptive names
- Organize by type/category
- Optimize before uploading

## Directory Creation

Necessary directories created during setup:

```bash
media/courses
media/blog
media/gallery
media/testimonials
media/admin
static/css
static/js
static/images
logs
```

## Git-Excluded Directories

- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `*.egg-info/` - Package files
- `build/`, `dist/` - Build files
- `media/` - User uploads
- `logs/` - Log files
- `.env` - Environment variables
- `db.sqlite3` - Database

## Backup Directories

Recommended backup locations:

- Database: `backups/database/`
- Media: `backups/media/`
- Logs: `backups/logs/`
- Configuration: `backups/config/`

---

**Document**: Directory Structure Documentation
**Project**: NCHSM Kikuyu Campus
**Updated**: 2024
