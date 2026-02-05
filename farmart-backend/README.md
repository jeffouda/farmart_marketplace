<p align="center">
  <img src="https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens" alt="JWT"/>
</p>

<h1 align="center">🐄 Farmart Backend API</h1>

<p align="center">
  <strong>A robust RESTful API powering Kenya's premier livestock e-commerce platform</strong>
</p>

<p align="center">
  Connecting livestock farmers directly to buyers with secure transactions, real-time inventory, and seamless order management.
</p>

---

## ✨ Features

- **🔐 Secure Authentication** - JWT-based auth with role-based access control (Farmer, Buyer, Admin)
- **🐑 Livestock Management** - Full CRUD operations with advanced filtering and search
- **📦 Order Processing** - Complete order lifecycle with status tracking
- **💳 Payment Integration** - M-Pesa payment support with escrow system
- **⚖️ Dispute Resolution** - Built-in dispute handling for buyer protection
- **📊 Analytics Dashboard** - Real-time metrics for farmers and admins

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Flask 2.x |
| **Database** | PostgreSQL with SQLAlchemy ORM |
| **Authentication** | Flask-JWT-Extended |
| **Validation** | Marshmallow |
| **Migrations** | Flask-Migrate (Alembic) |
| **Rate Limiting** | Flask-Limiter |
| **CORS** | Flask-CORS |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- pip or pipenv

### Installation

```bash
# Clone the repository
cd farmart_marketplace/farmart-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or using Pipenv
pipenv install
pipenv shell
```

### Environment Setup

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/farmart_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=86400

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
```

### Database Setup

```bash
# Initialize database
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### Run the Server

```bash
# Development mode
flask run

# Or with hot reload
flask run --debug

# The API will be available at http://localhost:5000
```

---

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/refresh` | Refresh token |
| POST | `/api/auth/logout` | User logout |

### Livestock Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/livestock` | List all available livestock | Public |
| GET | `/api/livestock/:id` | Get livestock details | Public |
| POST | `/api/livestock` | Create new listing | Farmer |
| PUT | `/api/livestock/:id` | Update listing | Farmer (owner) |
| DELETE | `/api/livestock/:id` | Delete listing | Farmer (owner) |

**Query Parameters for GET `/api/livestock`:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter by animal type (Goat, Cow, Sheep) |
| `breed` | string | Filter by breed |
| `min_price` | number | Minimum price filter |
| `max_price` | number | Maximum price filter |
| `location` | string | Filter by location/county |
| `sort_by` | string | Sort: `newest`, `price-low`, `price-high` |
| `page` | number | Page number (default: 1) |
| `per_page` | number | Items per page (default: 20) |

### Order Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/orders/my_orders` | Get user's orders | Required |
| POST | `/api/orders` | Create new order | Buyer |
| GET | `/api/orders/:id` | Get order details | Owner |
| PUT | `/api/orders/:id/status` | Update order status | Owner |

### Farmer Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/farmer/livestock` | Get farmer's listings |
| POST | `/api/v1/farmer/livestock` | Create listing |
| PUT | `/api/v1/farmer/livestock/:id` | Update listing |
| DELETE | `/api/v1/farmer/livestock/:id` | Delete listing |
| GET | `/api/v1/farmer/orders` | Get farmer's orders |
| GET | `/api/v1/farmer/analytics` | Dashboard analytics |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_routes.py -v
```

---

## 📁 Project Structure

```
farmart-backend/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py             # Configuration classes
│   ├── extensions.py         # Flask extensions
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Marshmallow schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py            # Public API routes
│   │   ├── auth.py           # Authentication routes
│   │   ├── farmer.py         # Farmer-specific routes
│   │   ├── buyer.py          # Buyer-specific routes
│   │   ├── admin.py          # Admin routes
│   │   └── payments.py       # Payment routes
│   ├── services/
│   │   └── escrow_manager.py # Escrow handling
│   └── utils/
│       └── decorators.py     # Role decorators
├── migrations/               # Database migrations
├── tests/                    # Test suite
├── requirements.txt
├── Pipfile
└── run.py                    # Application entry point
```

---

## 👥 Team

Built with ❤️ by the Farmart Development Team

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
