# NotesRoom Backend

A comprehensive Django REST Framework backend for managing educational documents, notes, and coursework. NotesRoom provides a centralized platform for students and instructors to organize and access study materials across different semesters and subjects.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [Running the Application](#running-the-application)
- [Email Notifications](#email-notifications)
- [Authentication](#authentication)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

NotesRoom is a backend service designed to streamline the management of educational documents and coursework. It allows administrators to organize materials by semesters and subjects, automatically notify students about new documents, and provides a seamless API for frontend applications to consume.

The system leverages Django's powerful ORM, REST Framework for API development, and Brevo for email notifications.

## ✨ Features

### Core Features
- **Document Management**: Upload and organize documents by semester and subject
- **User Authentication**: JWT-based authentication with OTP verification
- **Role-Based Access**: Different permissions for students, instructors, and administrators
- **Email Notifications**: Automated email alerts when new documents are uploaded
- **AI-Powered Features**: Chat with PDF documents and general chat capabilities
- **Google OAuth Integration**: Seamless login with Google accounts
- **CORS Support**: Cross-origin resource sharing for frontend integration

### Advanced Features
- **OTP Verification**: Multi-factor authentication support via Brevo email service
- **Document Ownership**: Track document ownership and upload history
- **Selective Notifications**: Choose whether to notify users when uploading documents
- **Token Refresh**: JWT token refresh mechanism for persistent sessions
- **Cloud Storage Support**: Integration with cloud storage services via django-storages

## 🛠️ Tech Stack

### Backend Framework
- **Django 5.1.7** - Web framework
- **Django REST Framework** - RESTful API development
- **Django Storages** - Cloud storage integration

### Authentication & Security
- **djangorestframework-simplejwt** - JWT token authentication
- **django-cors-headers** - CORS handling

### Database
- **PostgreSQL** (configured via environment variables)
- **dj-database-url** - Database URL parsing

### Email & Notifications
- **Brevo API** - Email service provider for OTP and bulk notifications

### Additional Libraries
- **python-dotenv** - Environment variable management
- **requests** - HTTP client library

## 📁 Project Structure

```
notesroom-backend/
├── core_api/                    # Django project configuration
│   ├── settings.py             # Project settings and configuration
│   ├── urls.py                 # URL routing configuration
│   ├── asgi.py                 # ASGI configuration
│   ├── wsgi.py                 # WSGI configuration
│   └── __init__.py
│
├── coursework/                  # Main application
│   ├── models.py               # Database models
│   ├── views.py                # API viewsets and views
│   ├── auth_views.py           # Authentication endpoints
│   ├── ai_views.py             # AI-powered endpoints
│   ├── serializers.py          # DRF serializers
│   ├── utils.py                # Utility functions
│   ├── admin.py                # Django admin configuration
│   ├── urls.py                 # App URL routing
│   ├── migrations/             # Database migrations
│   └── __init__.py
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Brevo account (for email services)
- Google OAuth credentials (optional, for Google login)
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd notesroom-backend
```

### 2. Create a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/notesroom_db

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Service (Brevo)
BREVO_API_KEY=your-brevo-api-key-here
BREVO_SENDER_EMAIL=notesroomofficial@gmail.com

# JWT Configuration
JWT_SECRET=your-jwt-secret-key-here
JWT_EXPIRATION_HOURS=24

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Cloud Storage (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

### 5. Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

## ⚙️ Configuration

### Django Settings

Key configurations in [core_api/settings.py](core_api/settings.py):

- **INSTALLED_APPS**: Includes `rest_framework`, `corsheaders`, `coursework`, and `storages`
- **CORS_ALLOW_ALL_ORIGINS**: Set to `True` for development (restrict in production)
- **REST_FRAMEWORK**: Configured with JWT authentication and pagination
- **FILE_UPLOAD_MAX_MEMORY_SIZE**: Configurable for file uploads

### Database Configuration

Database URL is parsed from environment variable:

```python
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}
```

Supports SQLite for development and PostgreSQL for production.

## 🔌 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | User registration with email |
| POST | `/api/auth/verify-otp/` | Verify OTP for email confirmation |
| POST | `/api/auth/resend-otp/` | Resend OTP code |
| POST | `/api/token/` | Obtain JWT token (login) |
| POST | `/api/token/refresh/` | Refresh JWT token |
| POST | `/api/auth/google-login/` | Google OAuth login |
| GET | `/api/auth/profile/` | Get user profile (authenticated) |

### Coursework Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/semesters/` | List all semesters |
| GET | `/api/semesters/{id}/` | Get specific semester |
| GET | `/api/subjects/` | List all subjects |
| GET | `/api/documents/` | List all documents |
| POST | `/api/documents/` | Upload new document (admin only) |
| GET | `/api/documents/{id}/` | Get specific document |
| DELETE | `/api/documents/{id}/` | Delete document (admin only) |

### AI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat-with-pdf/` | Chat with PDF documents |
| POST | `/api/ai/general-chat/` | General chat with AI |

## 📊 Database Models

### Semester
```python
- name (CharField): Unique semester identifier (e.g., "Semester 4")
```

### Subject
```python
- semester (ForeignKey): Associated semester
- name (CharField): Subject name (e.g., "iOS Development")
```

### Document
```python
- subject (ForeignKey): Associated subject
- title (CharField): Document title
- file (FileField): Uploaded document
- uploaded_at (DateTimeField): Upload timestamp
- owner (ForeignKey): Uploading administrator
- notify_users (BooleanField): Send notification to users on upload
```

### OTP
```python
- user (OneToOneField): Associated user
- code (CharField): 6-digit OTP code
- created_at (DateTimeField): Creation timestamp
- is_valid(): Check if OTP is valid (expires after 10 minutes)
```

### User
```python
- username (CharField): Unique username
- email (EmailField): Unique email address
- password (CharField): Hashed password
- is_staff (BooleanField): Admin status
- is_active (BooleanField): Account active status
```

## 📧 Email Notifications

### OTP Email Service
Brevo is used to send OTP codes for email verification:

```python
send_otp_via_brevo(email, otp_code)
```

### Document Notification Service
When a document is uploaded with `notify_users=True`, an automated email is sent to all registered students:

```python
send_new_document_notification(document_instance)
```

The notification includes:
- Document title
- Subject name
- Semester information
- Download/access instructions

**Note**: Email notifications are sent asynchronously via threading to avoid blocking the HTTP response.

## 🔐 Authentication

### JWT Authentication
The application uses JSON Web Tokens (JWT) for stateless authentication:

1. User obtains token via `/api/token/` endpoint
2. Token is included in the `Authorization` header: `Authorization: Bearer <token>`
3. Token can be refreshed using `/api/token/refresh/` endpoint
4. Token expiration is configured via `JWT_EXPIRATION_HOURS`

### OTP Verification
For enhanced security:

1. User registers with email
2. 6-digit OTP is sent via Brevo
3. OTP is verified and email is confirmed
4. User can now access the application

### Google OAuth
Users can authenticate using their Google account without registration.

## 🏃 Running the Application

### Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

### Create Test Data

```bash
python manage.py shell

# In the shell:
from coursework.models import Semester, Subject
semester = Semester.objects.create(name="Semester 4")
subject = Subject.objects.create(semester=semester, name="iOS Development")
```

### Run Tests

```bash
python manage.py test coursework
```

### Admin Panel

Access the Django admin at `http://localhost:8000/admin/` with your superuser credentials.

## 🌐 CORS Configuration

CORS is configured to allow all origins in development:

```python
CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['*']
```

**Important**: Restrict these in production:

```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

## 📝 Document Upload

### Upload Process

1. Authenticate with JWT token
2. Create semester and subject (if not exists)
3. POST to `/api/documents/` with:
   - `subject_id`: Subject identifier
   - `title`: Document title
   - `file`: Document file
   - `notify_users`: Boolean to send notifications

```bash
curl -X POST http://localhost:8000/api/documents/ \
  -H "Authorization: Bearer <token>" \
  -F "subject_id=1" \
  -F "title=Lecture Notes" \
  -F "file=@lecture.pdf" \
  -F "notify_users=true"
```

## 🤝 Contributing

### Development Guidelines

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -am 'Add new feature'`
3. Push to the branch: `git push origin feature/your-feature`
4. Submit a pull request

### Code Standards

- Follow PEP 8 style guide
- Write docstrings for all functions and classes
- Add tests for new features
- Update this README if adding new endpoints or features

## 🐛 Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify DATABASE_URL in `.env`
2. Ensure PostgreSQL service is running
3. Check database credentials

### Email Service Issues

If emails are not being sent:

1. Verify BREVO_API_KEY is correct
2. Ensure sender email is verified in Brevo
3. Check Brevo API status
4. Review application logs for errors

### CORS Issues

If frontend cannot access the API:

1. Check CORS_ALLOW_ALL_ORIGINS setting
2. Verify ALLOWED_HOSTS configuration
3. Ensure frontend is sending correct headers

### JWT Token Errors

If authentication fails:

1. Verify JWT_SECRET is set
2. Check token expiration
3. Ensure Authorization header format is correct: `Bearer <token>`

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Brevo Email API](https://www.brevo.com/api/)
- [JWT Authentication](https://github.com/jpadilla/django-rest-framework-simplejwt)

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

**Last Updated**: May 2026  
**Version**: 1.0.0  
**Maintainer**: NotesRoom Development Team
