# 🤖 EduBot - College Chatbot Application

A comprehensive Python Flask-based chatbot designed for college students to interact with and get answers related to faculty details, attendance records, upcoming events, group creation, file sharing, and more.

## ✨ Features

- **User Authentication** - Secure login/register system for students, faculty, and admin
- **Role-based Access Control** - Different permissions for students, faculty, and admin users
- **Intelligent Chatbot** - Pattern-matching based conversational AI
- **Faculty Information** - Search and view faculty details, departments, office hours
- **Attendance Tracking** - View personal attendance records and percentages
- **Event Management** - Upcoming events, holidays, and college calendar
- **File Sharing** - Upload/download syllabus, notes, and course materials
- **Group Chat** - Create study groups and project teams with real-time messaging
- **Motivational Quotes** - Daily inspiration for students
- **Admin Dashboard** - Complete CRUD operations for all data
- **Real-time Features** - WebSocket support for instant messaging

## 🛠️ Technology Stack

- **Backend**: Python 3.8+ with Flask framework
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
- **Real-time**: Flask-SocketIO for WebSocket support
- **Security**: Flask-WTF CSRF protection, Flask-Login, Werkzeug password hashing
- **Rate Limiting**: Flask-Limiter for API protection

## 📋 Prerequisites

Before running EduBot, ensure you have:

1. **Python 3.8 or higher** installed
2. **MySQL 8.0** server installed and running
3. **Git** (optional, for cloning)

## ⚡ Quick Setup

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd EduBot
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database
```sql
-- Login to MySQL as root
mysql -u root -p

-- Create database
CREATE DATABASE edubot_db;

-- Create user (optional, for security)
CREATE USER 'edubot_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON edubot_db.* TO 'edubot_user'@'localhost';
FLUSH PRIVILEGES;

-- Import schema
USE edubot_db;
SOURCE db/schema.sql;
```

### 5. Configure Environment Variables
Edit the `.env` file or set environment variables:
```bash
# Database settings
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=edubot_db

# Security
SECRET_KEY=your-secret-key-here

# Flask settings
FLASK_ENV=development
FLASK_DEBUG=true
```

### 6. Run the Application
```bash
python run.py
```

The application will start on `http://127.0.0.1:5000`

## 🔐 Default Login Credentials

**Admin Access:**
- Username: `admin`
- Password: `admin123`

**Student Access:**
- Register a new account at `/register`

## 📁 Project Structure

```
EduBot/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── models/                     # Database models
│   │   ├── user.py                # User model with authentication
│   │   ├── faculty.py             # Faculty information
│   │   ├── course.py              # Course management
│   │   ├── attendance.py          # Attendance tracking
│   │   ├── event.py               # Events and holidays
│   │   ├── chat_log.py            # Chat conversation logs
│   │   └── ...                    # Other models
│   ├── routes/                     # Route blueprints
│   │   ├── auth.py                # Authentication routes
│   │   ├── chat.py                # Chatbot interface
│   │   ├── admin.py               # Admin dashboard
│   │   └── ...                    # Other route modules
│   ├── chatbot/                    # Chatbot engine
│   │   ├── intents.py             # Intent definitions
│   │   └── handlers.py            # Response handlers
│   ├── templates/                  # Jinja2 templates
│   │   ├── auth/                  # Login/register pages
│   │   ├── chat/                  # Chat interface
│   │   ├── admin/                 # Admin dashboard
│   │   └── ...                    # Other template folders
│   └── static/                     # Static assets
│       ├── css/                   # Custom stylesheets
│       ├── js/                    # JavaScript files
│       ├── uploads/               # File uploads
│       └── assets/                # Images, icons, etc.
├── config/
│   └── config.py                  # Application configuration
├── db/
│   └── schema.sql                 # Database schema
├── migrations/                     # Database migrations
├── requirements.txt               # Python dependencies
├── run.py                         # Application entry point
├── .env                          # Environment variables
└── README.md                     # This file
```

## 🚀 Development Roadmap

### Phase 1: Foundation (Completed)
- ✅ Project structure setup
- ✅ Database schema design
- ✅ User authentication system
- ✅ Basic login/register functionality
- ✅ Flask app configuration

### Phase 2: Core Features (Next Steps)
- [ ] Chatbot engine with intent recognition
- [ ] Faculty information management
- [ ] Attendance tracking system
- [ ] Event management
- [ ] File upload/download system

### Phase 3: Advanced Features
- [ ] Real-time group chat with SocketIO
- [ ] Admin dashboard with full CRUD
- [ ] Advanced chatbot responses
- [ ] File preview and management
- [ ] Push notifications

### Phase 4: Enhancement
- [ ] Mobile-responsive design
- [ ] API documentation
- [ ] Unit and integration tests
- [ ] Performance optimization
- [ ] Deployment configuration

## 🔧 Development Commands

```bash
# Install new dependencies
pip install package_name
pip freeze > requirements.txt

# Database operations
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Run with different configurations
FLASK_ENV=production python run.py
```

## 🐛 Troubleshooting

### Common Issues:

1. **MySQL Connection Error**
   - Ensure MySQL server is running
   - Check database credentials in `.env`
   - Verify database exists

2. **Import Errors**
   - Activate virtual environment
   - Install all dependencies: `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change port in `.env`: `FLASK_PORT=5001`
   - Or kill process using the port

4. **Templates Not Found**
   - Ensure you're running from the project root directory
   - Check template file paths

## 📝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Support

For support, email [your-email@domain.com] or create an issue in the repository.

---

**EduBot** - Making college life easier, one conversation at a time! 🎓✨
