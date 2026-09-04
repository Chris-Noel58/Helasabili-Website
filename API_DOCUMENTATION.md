# API Documentation - NCHSM Kikuyu Campus

## Overview

This document describes the routes, endpoints, and API structure for the NCHSM Kikuyu Campus website system.

## Base URL

Development: `http://localhost:8000`
Production: `https://yourdomain.com`

## Public Website Routes

### Home Page
- **URL**: `/`
- **Method**: GET
- **Description**: Display home page with hero section, featured courses, testimonials, and news
- **Response**: HTML page

### About Page
- **URL**: `/about/`
- **Method**: GET
- **Description**: Display about page with college information
- **Response**: HTML page

### Courses

#### List All Courses
- **URL**: `/courses/`
- **Method**: GET
- **Query Parameters**:
  - `search` (optional): Search by course name or description
  - `page` (optional): Page number for pagination
- **Description**: Display list of all active courses
- **Response**: HTML page with course listings

#### Course Detail
- **URL**: `/course/<slug>/`
- **Method**: GET
- **Parameters**:
  - `slug`: Course slug (e.g., `nursing-science`)
- **Description**: Display detailed course information
- **Response**: HTML page with course details, related courses, and application form

### Blog/News

#### Blog List
- **URL**: `/blog/`
- **Method**: GET
- **Query Parameters**:
  - `search` (optional): Search by blog title or content
  - `page` (optional): Page number for pagination
- **Description**: Display list of published blog posts
- **Response**: HTML page with blog posts

#### Blog Post Detail
- **URL**: `/blog/<slug>/`
- **Method**: GET
- **Parameters**:
  - `slug`: Blog post slug
- **Description**: Display full blog post content
- **Response**: HTML page with blog post and related articles

### Gallery
- **URL**: `/gallery/`
- **Method**: GET
- **Query Parameters**:
  - `category` (optional): Filter by image category (classroom, event, graduation, lab, campus)
  - `page` (optional): Page number for pagination
- **Description**: Display gallery images
- **Response**: HTML page with image gallery

### Testimonials
- **URL**: `/testimonials/`
- **Method**: GET
- **Query Parameters**:
  - `page` (optional): Page number for pagination
- **Description**: Display student testimonials
- **Response**: HTML page with testimonials

### Application Form

#### Get Application Form
- **URL**: `/apply/`
- **Method**: GET
- **Description**: Display application form page
- **Response**: HTML page with application form

#### Submit Application
- **URL**: `/apply/`
- **Method**: POST
- **Request Body**:
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+254712345678",
  "course": 1,
  "message": "I want to study nursing"
}
```
- **Description**: Submit student application
- **Response**: Redirect to home page with success message
- **Errors**:
  - 400: Invalid form data
  - 500: Server error

### Contact Page
- **URL**: `/contact/`
- **Method**: GET
- **Description**: Display contact page
- **Response**: HTML page with contact form and information

### Newsletter Subscription
- **URL**: `/newsletter/subscribe/`
- **Method**: POST
- **Request Body**:
```json
{
  "email": "user@example.com"
}
```
- **Description**: Subscribe to newsletter
- **Response**: Redirect to referrer page with success message

## Dashboard Routes

### Authentication

#### Admin Login
- **URL**: `/dashboard/login/`
- **Method**: GET, POST
- **Request Body (POST)**:
```json
{
  "username": "admin",
  "password": "password",
  "remember_me": true
}
```
- **Response**: Redirect to dashboard on success
- **Authentication**: Not required (public page)

#### Admin Logout
- **URL**: `/dashboard/logout/`
- **Method**: GET
- **Response**: Redirect to login page
- **Authentication**: Required

### Dashboard Home
- **URL**: `/dashboard/`
- **Method**: GET
- **Description**: Display dashboard statistics and recent data
- **Response**: HTML page with dashboard information
- **Authentication**: Required (admin only)

### Courses Management

#### List Courses
- **URL**: `/dashboard/courses/`
- **Method**: GET
- **Query Parameters**:
  - `search` (optional): Search by course name
  - `page` (optional): Page number
- **Response**: HTML page with courses table
- **Authentication**: Required (admin only)

#### Create Course
- **URL**: `/dashboard/courses/create/`
- **Method**: GET, POST
- **Request Body (POST)**:
```json
{
  "title": "Nursing Science",
  "description": "3-year nursing program",
  "duration": "3 Years",
  "intake_period": "january",
  "fees": 250000,
  "featured_image": "file",
  "is_active": true,
  "order": 1
}
```
- **Response**: Redirect to courses list on success
- **Authentication**: Required (admin only)

#### Update Course
- **URL**: `/dashboard/courses/<id>/edit/`
- **Method**: GET, POST
- **Request Body**: Same as create
- **Response**: Redirect to courses list on success
- **Authentication**: Required (admin only)

#### Delete Course
- **URL**: `/dashboard/courses/<id>/delete/`
- **Method**: POST
- **Response**: Redirect to courses list
- **Authentication**: Required (admin only)

### Blog Management

#### List Blog Posts
- **URL**: `/dashboard/blog/`
- **Method**: GET
- **Query Parameters**:
  - `search` (optional): Search by title or content
  - `status` (optional): Filter by status (draft, published, archived)
  - `page` (optional): Page number
- **Response**: HTML page with blog posts table
- **Authentication**: Required (admin only)

#### Create Blog Post
- **URL**: `/dashboard/blog/create/`
- **Method**: GET, POST
- **Request Body (POST)**:
```json
{
  "title": "College News",
  "featured_image": "file",
  "content": "Blog content here",
  "excerpt": "Short summary",
  "author": "Admin Name",
  "status": "published",
  "is_featured": false
}
```
- **Response**: Redirect to blog list on success
- **Authentication**: Required (admin only)

#### Update Blog Post
- **URL**: `/dashboard/blog/<id>/edit/`
- **Method**: GET, POST
- **Request Body**: Same as create
- **Response**: Redirect to blog list on success
- **Authentication**: Required (admin only)

#### Delete Blog Post
- **URL**: `/dashboard/blog/<id>/delete/`
- **Method**: POST
- **Response**: Redirect to blog list
- **Authentication**: Required (admin only)

### Testimonials Management

#### List Testimonials
- **URL**: `/dashboard/testimonials/`
- **Method**: GET
- **Query Parameters**:
  - `search` (optional): Search by name or course
  - `page` (optional): Page number
- **Response**: HTML page with testimonials table
- **Authentication**: Required (admin only)

#### Create Testimonial
- **URL**: `/dashboard/testimonials/create/`
- **Method**: GET, POST
- **Request Body (POST)**:
```json
{
  "name": "Student Name",
  "course": "Nursing Science",
  "message": "Great college experience",
  "photo": "file",
  "rating": 5,
  "is_active": true,
  "order": 1
}
```
- **Response**: Redirect to testimonials list on success
- **Authentication**: Required (admin only)

#### Update Testimonial
- **URL**: `/dashboard/testimonials/<id>/edit/`
- **Method**: GET, POST
- **Request Body**: Same as create
- **Response**: Redirect to testimonials list on success
- **Authentication**: Required (admin only)

#### Delete Testimonial
- **URL**: `/dashboard/testimonials/<id>/delete/`
- **Method**: POST
- **Response**: Redirect to testimonials list
- **Authentication**: Required (admin only)

### Gallery Management

#### List Gallery Images
- **URL**: `/dashboard/gallery/`
- **Method**: GET
- **Query Parameters**:
  - `search` (optional): Search by title
  - `category` (optional): Filter by category
  - `page` (optional): Page number
- **Response**: HTML page with gallery images
- **Authentication**: Required (admin only)

#### Upload Image
- **URL**: `/dashboard/gallery/upload/`
- **Method**: GET, POST
- **Request Body (POST)**:
```json
{
  "title": "Campus Building",
  "image": "file",
  "category": "campus",
  "description": "Image description",
  "is_active": true,
  "order": 1
}
```
- **Response**: Redirect to gallery list on success
- **Authentication**: Required (admin only)

#### Update Image
- **URL**: `/dashboard/gallery/<id>/edit/`
- **Method**: GET, POST
- **Request Body**: Same as upload
- **Response**: Redirect to gallery list on success
- **Authentication**: Required (admin only)

#### Delete Image
- **URL**: `/dashboard/gallery/<id>/delete/`
- **Method**: POST
- **Response**: Redirect to gallery list
- **Authentication**: Required (admin only)

### Applications Management

#### List Applications
- **URL**: `/dashboard/applications/`
- **Method**: GET
- **Query Parameters**:
  - `search` (optional): Search by name, email, phone
  - `status` (optional): Filter by status
  - `course` (optional): Filter by course ID
  - `page` (optional): Page number
- **Response**: HTML page with applications table
- **Authentication**: Required (admin only)

#### Application Detail
- **URL**: `/dashboard/applications/<id>/`
- **Method**: GET, POST
- **Request Body (POST)**:
```json
{
  "status": "reviewed"
}
```
- **Response**: HTML page with application details / redirect on POST
- **Authentication**: Required (admin only)

#### Export Applications to CSV
- **URL**: `/dashboard/applications/export/csv/`
- **Method**: GET
- **Response**: CSV file download
- **Authentication**: Required (admin only)

### About Page Management

#### Edit About Page
- **URL**: `/dashboard/about/edit/`
- **Method**: GET, POST
- **Request Body (POST)**:
```json
{
  "title": "About NCHSM",
  "history": "College history text",
  "mission": "Mission statement",
  "vision": "Vision statement",
  "values": "Values description",
  "principal_message": "Principal's message",
  "principal_name": "Principal Name",
  "principal_image": "file",
  "campus_description": "Campus description",
  "location": "Kikuyu, Kenya",
  "established_year": 2024
}
```
- **Response**: HTML form / redirect on success
- **Authentication**: Required (admin only)

### Contact Information Management

#### Edit Contact Info
- **URL**: `/dashboard/contact/edit/`
- **Method**: GET, POST
- **Request Body (POST)**:
```json
{
  "phone_primary": "+254712345678",
  "phone_secondary": "+254787654321",
  "email": "info@nchsm.ac.ke",
  "email_alternative": "admissions@nchsm.ac.ke",
  "address": "Street address",
  "postal_code": "00100",
  "city": "Kikuyu",
  "country": "Kenya",
  "facebook": "https://facebook.com/nchsm",
  "twitter": "https://twitter.com/nchsm",
  "linkedin": "https://linkedin.com/company/nchsm",
  "instagram": "https://instagram.com/nchsm",
  "youtube": "https://youtube.com/nchsm",
  "latitude": -1.2921,
  "longitude": 36.7274,
  "opening_hours": "Monday - Friday: 8:00 AM - 5:00 PM"
}
```
- **Response**: HTML form / redirect on success
- **Authentication**: Required (admin only)

## Error Responses

### 404 Not Found
```html
<error page with 404 message>
```

### 500 Server Error
```html
<error page with 500 message>
```

### Form Validation Error
Returns form with error messages highlighted

## Status Codes

- `200`: OK - Request successful
- `301/302`: Redirect - Page moved or post processed
- `400`: Bad Request - Invalid form data
- `404`: Not Found - Page doesn't exist
- `500`: Server Error - Internal server error

## Authentication

All dashboard routes require:
1. User must be logged in
2. User must be staff/admin user
3. CSRF token must be valid for POST requests

## Rate Limiting

No rate limiting is currently implemented. For production, consider implementing rate limiting for:
- Application submissions
- Newsletter subscriptions
- Contact form submissions

## File Upload Limits

- Maximum upload size: 20MB (configurable in settings)
- Allowed image formats: JPG, PNG, GIF
- Images are automatically optimized on upload

## CORS

CORS is configured for development but should be restricted in production.

## Pagination

- Default page size: 10-20 items per page
- Configurable in Django settings

## Caching

No caching is currently implemented. For production, consider adding:
- Browser caching headers
- Django cache framework
- Redis caching

## Security

All routes implement:
- CSRF protection
- SQL injection prevention (ORM)
- XSS protection
- Admin authentication
- Password hashing
- Secure session handling

## Examples

### Submit Application via Form
```html
<form method="POST" action="/apply/">
    {% csrf_token %}
    <input type="text" name="full_name" required>
    <input type="email" name="email" required>
    <input type="tel" name="phone" required>
    <select name="course" required>
        <option value="1">Nursing Science</option>
    </select>
    <textarea name="message"></textarea>
    <button type="submit">Apply</button>
</form>
```

### Search Courses
```html
<form method="GET" action="/courses/">
    <input type="text" name="search" placeholder="Search courses...">
    <button type="submit">Search</button>
</form>
```

## Support

For API support and questions, contact the development team.
