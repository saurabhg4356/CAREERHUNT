# CareerHunt — Setup & Installation Guide

## 1. System Requirements
- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** Version 3.13 (or 3.11+)
- **Git:** Version 2.30+
- **Database:** SQLite (default for development), PostgreSQL 15+ (for production)

---

## 2. Step-by-Step Installation

### 2.1 Clone / Access Repository
```bash
cd c:\CAREERHUNT
```

### 2.2 Activate Virtual Environment
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2.3 Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```

### 2.5 Run Database Migrations
```powershell
python manage.py migrate
```

### 2.6 Verify Project Health
```powershell
python manage.py check
python -m pytest
```

### 2.7 Run Development Server
```powershell
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your web browser.
