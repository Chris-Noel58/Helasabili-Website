# NCHSM Kikuyu Campus - Quick Start Guide

## 5-Minute Setup

### Step 1: Download & Extract
- Download the project files
- Extract to your desired location
- Open terminal/command prompt in the project folder

### Step 2: Install Python & Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Configure Database

Create `.env` file in project root:

```env
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### Step 4: Initialize Database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

When prompted, enter:
- Username: admin
- Email: admin@nchsm.ac.ke
- Password: (your choice)

### Step 5: Start Server

```bash
python manage.py runserver
```

### Step 6: Access the Website

- **Website**: http://localhost:8000
- **Dashboard**: http://localhost:8000/dashboard/login/
- **Django Admin**: http://localhost:8000/admin/

Login with the credentials you created in Step 4.

## First Steps as Admin

1. **Add Contact Information**
   - Go to Dashboard → Contact Info
   - Fill in phone, email, address, and social media links
   - Save

2. **Update About Page**
   - Go to Dashboard → About Page
   - Add college history, mission, vision, values
   - Add principal's information
   - Save

3. **Add Courses**
   - Go to Dashboard → Courses → Add New Course
   - Fill course details
   - Upload featured image
   - Save

4. **Upload Gallery Images**
   - Go to Dashboard → Gallery → Upload Image
   - Select category
   - Upload images
   - Save

5. **Write Blog Posts**
   - Go to Dashboard → Blog Posts → Write New Post
   - Create engaging content
   - Publish

6. **View Applications**
   - Applications appear automatically when students apply
   - Go to Dashboard → Applications
   - Review and update status

## Common Tasks

### Change Website Title
Edit `templates/partials/navbar.html` - Change the NCHSM text

### Change Colors
Edit `static/css/style.css` - Modify CSS variables at the top

### Add New Course
Dashboard → Courses → Add New Course → Fill details → Save

### Create Blog Post
Dashboard → Blog Posts → Write New Post → Fill details → Publish

### Export Applications
Dashboard → Applications → Click "Export CSV"

### Back Up Database
```bash
cp db.sqlite3 db.sqlite3.backup
```

### Update Application
```bash
git pull
pip install -r requirements.txt
python manage.py migrate
```

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Permission Denied (Linux/Mac)
```bash
chmod +x manage.py
chmod -R 755 media/
```

### Database Locked
```bash
rm db.sqlite3
python manage.py migrate
```

## File Locations

- **Website Templates**: `templates/website/`
- **Dashboard Templates**: `templates/dashboard/`
- **Static Files**: `static/`
- **Uploaded Files**: `media/`
- **Database**: `db.sqlite3` (development only)

## Deployment Preparation

Before going live:

1. Change `DEBUG = False` in `.env`
2. Update `SECRET_KEY` with a strong random string
3. Set `ALLOWED_HOSTS` to your domain
4. Configure production database (PostgreSQL recommended)
5. Set up HTTPS/SSL certificate
6. Configure email settings for contact forms
7. Create admin superuser for production
8. Back up all data

## Getting Help

1. Check README.md for detailed documentation
2. Review Django documentation: https://docs.djangoproject.com/
3. Check Bootstrap docs: https://getbootstrap.com/docs/
4. Review inline code comments

## Next Steps

1. Customize colors and branding in CSS
2. Upload college logo and images
3. Add all courses
4. Create initial blog posts
5. Configure email notifications
6. Set up social media links
7. Test all forms
8. Create a staging environment for testing

Happy coding! 🚀
