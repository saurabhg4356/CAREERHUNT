# CareerHunt — Technology Stack & Dependencies

## 1. Technology Rationale

### 1.1 Backend
- **Python 3.13:** Latest stable Python runtime offering improved performance and modern typing.
- **Django 5.1+:** Robust web framework with built-in ORM, secure authentication, session management, CSRF protection, and management command ecosystem.
- **Django REST Framework (DRF) 3.15+:** Standard for enterprise-grade REST APIs, serializers, viewsets, and token/session authentication.
- **django-filter 24.3+:** Declarative, robust URL-to-QuerySet filtering for search and faceted browsing.
- **django-environ 0.11+:** Twelve-factor environment variable loading from `.env` files with type casting.
- **Pillow 10.4+:** Image processing for company logos and visual assets.
- **Whitenoise 6.7+:** Efficient static file serving directly from the WSGI/ASGI application.

### 1.2 Data Collection & Parsing
- **Requests 2.32+:** HTTP client for API and feed fetching with timeout, user-agent configuration, and retry adapters.
- **BeautifulSoup4 & lxml:** HTML and XML parsing for structured feed analysis and clean text extraction.
- **Feedparser 6.0+:** Robust RSS/Atom feed syndication reader.

### 1.3 Testing
- **Pytest & pytest-django:** Modern, fixture-driven testing framework ensuring fast execution and deep assertions.

### 1.4 Frontend Design System
- **HTML5 & Semantic Markup:** Fully accessible structure.
- **CSS3 with Tailwind CSS & Bootstrap Utilities:** Modern UI design with clean cards, badges, modal dialogs, responsive grids, and dark/light accents.
- **Vanilla JavaScript:** Micro-interactions (save toggles, dynamic deadline countdowns, filter drawer, toast notifications) without heavy SPA runtime overhead.

---

## 2. Environment Variables Specification

The system uses `.env` files parsed by `django-environ`. See `.env.example` for details.
Key environment parameters:
- `SECRET_KEY`: Cryptographic signing key (must be kept secret in production).
- `DEBUG`: Boolean flag (`True` for local development, `False` for production).
- `ALLOWED_HOSTS`: Comma-separated list of host/domain names.
- `DATABASE_URL`: Connection string (defaults to `sqlite:///db.sqlite3` locally, PostgreSQL in staging/production).
- `COLLECTOR_USER_AGENT`: Descriptive User-Agent string identifying the platform when fetching feeds.
