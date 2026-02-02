# FarmAT Project Update - Backend Schema Fix

## Changes Summary (Merged to `main`)

Hi team! The following changes have been merged to the `main` branch:

### Backend Changes:
- ✅ Fixed marshmallow schema import errors (removed string model references)
- ✅ Added new schemas for User, Livestock, Order, Payment, Dispute models
- ✅ Integrated Flask-Migrate for database version control
- ✅ Updated Pipfile with new dependencies

### Key Files Modified:
- [`farmart-backend/app/schemas.py`](farmart-backend/app/schemas.py) - New marshmallow schemas
- [`farmart-backend/app/extensions.py`](farmart-backend/app/extensions.py) - Added Flask-Migrate
- [`farmart-backend/app/__init__.py`](farmart-backend/app/__init__.py) - Initialize migrations
- [`farmart-backend/Pipfile`](farmart-backend/Pipfile) - New dependencies

---

## Steps for Team Members

Run these commands in your terminal to update your local environment:

### 1. Switch to main branch and pull latest changes:
```bash
cd /home/jeff/phase5/FARMAT
git checkout main
git pull origin main
```

### 2. Install new backend dependencies:
```bash
cd farmart-backend
pipenv install flask-marshmallow marshmallow-sqlalchemy
```

### 3. Initialize Flask-Migrate (first time only):
```bash
pipenv run flask db init
```

### 4. Verify the backend works:
```bash
pipenv run python -c "from app import create_app, db; from app.schemas import UserSchema; app = create_app(); print('Backend Logic & Schemas Verified!')"
```

Expected output: `Backend Logic & Schemas Verified!`

### 5. Update the frontend:
```bash
cd ../farmart-frontend
npm install
npm run dev
```

---

## Troubleshooting

### If you get import errors:
Make sure you installed the new dependencies:
```bash
pipenv install flask-marshmallow marshmallow-sqlalchemy
```

### If Flask-Migrate asks for database URL:
The `.env` file should have:
```env
DATABASE_URL=sqlite:///farmart_dev.db
SQLALCHEMY_DATABASE_URI=sqlite:///farmart_dev.db
```

### If you already have a migrations folder:
Skip the `pipenv run flask db init` command - just run:
```bash
pipenv run flask db upgrade
```

---




