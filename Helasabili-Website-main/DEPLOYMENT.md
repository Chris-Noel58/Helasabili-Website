# DEPLOYMENT GUIDE FOR PRODUCTION

## Pre-Deployment Checklist

### Security
- [ ] Change SECRET_KEY to a strong random value
- [ ] Set DEBUG = False
- [ ] Set ALLOWED_HOSTS correctly
- [ ] Enable HTTPS/SSL certificates
- [ ] Set SECURE_SSL_REDIRECT = True
- [ ] Set SESSION_COOKIE_SECURE = True
- [ ] Set CSRF_COOKIE_SECURE = True

### Database
- [ ] Set up PostgreSQL (recommended) or MySQL
- [ ] Create database and user
- [ ] Test database connection
- [ ] Run migrations
- [ ] Create superuser

### Email
- [ ] Configure SMTP settings
- [ ] Test email sending
- [ ] Set up email templates

### Backups
- [ ] Set up automated database backups
- [ ] Set up media file backups
- [ ] Document backup procedure

## Deployment Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install gunicorn
pip install psycopg2-binary  # For PostgreSQL
```

### 2. Configure Production Settings
Update `.env`:
```env
SECRET_KEY=your-very-secure-random-key-minimum-50-chars
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=nchskikuyu
DB_USER=nchsm_user
DB_PASSWORD=strong-password
DB_HOST=localhost
DB_PORT=5432

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-specific-password
```

### 3. Prepare Database
```bash
python manage.py migrate --settings=nchskikuyu.settings
python manage.py createsuperuser --settings=nchskikuyu.settings
```

### 4. Collect Static Files
```bash
python manage.py collectstatic --noinput --settings=nchskikuyu.settings
```

### 5. Set Permissions
```bash
# Create app user
sudo useradd -m -s /bin/bash nchsm

# Set permissions
sudo chown -R nchsm:nchsm /path/to/nchskikuyu
sudo chmod -R 755 /path/to/nchskikuyu
sudo chmod -R 770 /path/to/nchskikuyu/media
sudo chmod -R 770 /path/to/nchskikuyu/staticfiles
```

### 6. Configure Gunicorn
Create `/etc/systemd/system/nchsm.service`:

```ini
[Unit]
Description=NCHSM Kikuyu Campus Django Application
After=network.target

[Service]
Type=notify
User=nchsm
WorkingDirectory=/path/to/nchskikuyu
ExecStart=/path/to/nchskikuyu/venv/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --bind unix:/path/to/nchskikuyu/nchsm.sock \
    nchskikuyu.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nchsm
sudo systemctl start nchsm
```

### 7. Configure Nginx
Create `/etc/nginx/sites-available/nchsm`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # Logging
    access_log /var/log/nginx/nchsm_access.log;
    error_log /var/log/nginx/nchsm_error.log;
    
    # Maximum upload size
    client_max_body_size 20M;
    
    # Proxy settings
    location / {
        proxy_pass http://unix:/path/to/nchskikuyu/nchsm.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /path/to/nchskikuyu/staticfiles/;
        expires 30d;
    }
    
    # Media files
    location /media/ {
        alias /path/to/nchskikuyu/media/;
        expires 7d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/nchsm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Install SSL Certificate
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

## Database Migrations

```bash
# Create migrations
python manage.py makemigrations --settings=nchskikuyu.settings

# Apply migrations
python manage.py migrate --settings=nchskikuyu.settings
```

## Backup Strategy

### Automatic Daily Backup
Create `/home/nchsm/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/nchskikuyu"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump nchskikuyu > $BACKUP_DIR/db_$DATE.sql

# Media backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /path/to/nchskikuyu/media/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /home/nchsm/backup.sh
```

## Monitoring

### Check Application Status
```bash
sudo systemctl status nchsm
journalctl -u nchsm -f
```

### Check Database
```bash
psql -U nchsm_user -d nchskikuyu
# SELECT * FROM core_application;
```

### Check Nginx
```bash
sudo systemctl status nginx
tail -f /var/log/nginx/nchsm_error.log
```

## Scaling

For high traffic:

1. Use multiple Gunicorn workers:
```ini
ExecStart=/path/to/nchskikuyu/venv/bin/gunicorn \
    --workers 8 \
    --worker-class sync \
    --max-requests 1000 \
    --bind unix:/path/to/nchskikuyu/nchsm.sock \
    nchskikuyu.wsgi:application
```

2. Add Redis caching
3. Use CDN for static files
4. Database optimization
5. Load balancing

## Maintenance

### Update Django
```bash
pip install --upgrade django
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart nchsm
```

### Database Optimization
```bash
python manage.py dbshell
VACUUM ANALYZE;
```

## Support

For issues:
1. Check logs: `journalctl -u nchsm -f`
2. Check Nginx: `sudo nginx -t`
3. Restart service: `sudo systemctl restart nchsm`
4. Check database connection

## Emergency Procedures

### Emergency Restore
```bash
# Restore database
psql -U nchsm_user -d nchskikuyu < backup.sql

# Restore media
tar -xzf media_backup.tar.gz
```

### Emergency Downtime
```bash
# Create maintenance page
# Redirect all requests to maintenance page
# Fix issue
# Restore service
```

## Post-Deployment

1. Test all functionality
2. Monitor logs for errors
3. Test email notifications
4. Test file uploads
5. Monitor performance
6. Set up monitoring alerts
7. Document issues and fixes
