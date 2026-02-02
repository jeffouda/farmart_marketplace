# FarmAT Backend - Environment Setup Guide

This guide will help you set up your development environment for the FarmAT project.

---

## Prerequisites

### Required Software

| Software | Version | Description |
|----------|---------|-------------|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| PostgreSQL | 14+ | Database |
| Git | - | Version control |

---

## 1. Database Setup (PostgreSQL)

### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### Create Database and User

```bash
sudo -u postgres psql

CREATE DATABASE farmart_db;
CREATE USER farmart_user WITH ENCRYPTED PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE farmart_db TO farmart_user;
ALTER DATABASE farmart_db OWNER TO farmart_user;
GRANT ALL ON SCHEMA public TO farmart_user;
\q
```

---

## 2. Backend Setup (Flask)

### Clone and Navigate

```bash
cd /path/to/your/projects
git clone <your-repo-url>
cd farmart-backend
```

### Create Virtual Environment

```bash
pipenv shell

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in `farmart-backend/`:

```env
# Database
DATABASE_URL=postgresql://farmart_user:your_password_here@localhost:5432/farmart_db

# JWT Secret
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=86400

# M-Pesa Configuration
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_PASSKEY=your_passkey
MPESA_BUSINESS_SHORT_CODE=your_business_short_code
MPESA_CALLBACK_URL=https://your-domain.com/api/payments/callback/mpesa
MPESA_ENVIRONMENT=sandbox  # Use 'production' for live

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

### Initialize Database

```bash
# Create all tables
flask db upgrade

# Or using Python directly
python -c "from app import create_app, db; app = create_app('development'); app.app_context().push(); db.create_all()"
```

### Run Backend Server

```bash
python run.py
```

**Backend URL:** `http://localhost:5000`

### Test Backend

```bash
pytest tests/ -v
```

---

## 3. Frontend Setup (React + Vite)

### Navigate to Frontend

```bash
cd ../farmart-frontend
```

### Install Dependencies

```bash
npm install
```

### Configure Environment Variables

Create `.env` file in `farmart-frontend/`:

```env
VITE_API_URL=http://localhost:5000/api
```

### Run Frontend Dev Server

```bash
npm run dev
```

**Frontend URL:** `http://localhost:3000`

### Build for Production

```bash
npm run build
```

---

## 4. API Testing with Postman

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |

**Register Request:**
```json
{
  "email": "test@example.com",
  "password": "SecurePass123",
  "phone_number": "254700000000",
  "first_name": "John",
  "last_name": "Doe",
  "role": "farmer"
}
```

**Login Request:**
```json
{
  "email": "test@example.com",
  "password": "SecurePass123"
}
```

### Livestock Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/buyer/search?species=cattle` | Search livestock |
| GET | `/api/farmer/livestock` | Get farmer's livestock |
| POST | `/api/farmer/livestock` | Add new livestock |

---

## 5. M-Pesa Sandbox Setup

1. Create account at https://developer.safaricom.co.ke
2. Go to "My Apps" and create a new app
3. Copy Consumer Key and Consumer Secret to `.env`
4. Use sandbox environment for testing

> **Note:** Use a test phone number starting with `2547...` or `2541...` for STK Push

---

## 6. Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Module not found" errors | Activate virtual environment and reinstall: `pip install -r requirements.txt` |
| Database connection errors | Verify PostgreSQL is running and check `DATABASE_URL` in `.env` |
| CORS errors | Ensure frontend URL is correctly configured in `app/config.py` |
| M-Pesa callback not working | Use ngrok for local testing: `ngrok http 5000` |

---

## 7. Development Workflow

### Git Commands

```bash
# Create new branch
git checkout -b feature/your-feature

# Stage and commit changes
git add .
git commit -m "Add your feature"

# Push to remote
git push origin feature/your-feature

# Pull latest changes
git pull main
```

### Code Style

- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Run linters before committing

---

## 8. Project Structure

```
FARMAT/
├── farmart-backend/              # Flask Backend
│   ├── app/
│   │   ├── __init__.py           # App factory
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── config.py             # Configuration
│   │   ├── routes/               # API endpoints
│   │   ├── services/             # Business logic
│   │   └── utils/                # Helpers
│   ├── migrations/               # Database migrations
│   ├── tests/                    # Unit tests
│   ├── requirements.txt          # Python dependencies
│   └── run.py                    # Entry point
│
└── farmart-frontend/             # React Frontend
    ├── src/
    │   ├── components/           # Reusable UI components
    │   ├── features/             # Redux slices
    │   ├── pages/                # Page components
    │   ├── store/                # Redux store
    │   └── services/             # API service
    ├── package.json              # Node dependencies
    └── vite.config.js            # Vite configuration
```

---

## 9. Useful Commands

### Backend

```bash
# Run with debug mode
python run.py

# Run tests
pytest

# Check code quality
flake8 app/ --max-line-length=100
```

### Frontend

```bash
# Install new dependency
npm install package-name

# Run linter
npm run lint

# Build for production
npm run build
```

---

## 10. Getting Help

- Check existing issues on GitHub
- Review API documentation in code comments
- Ask team members for clarification

---

**Happy Coding! 🚀**
