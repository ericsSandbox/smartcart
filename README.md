# SmartCart

A smart grocery planning and budget management application that helps households manage their shopping lists, pantry inventory, and grocery budgets efficiently.

## Features

- 🏠 **Household Management**
  - Create and manage household profiles
  - Add multiple household members
  - Set monthly grocery budgets

- 📝 **Shopping Lists**
  - Create multiple shopping lists
  - Add items with quantities and units
  - Share lists between household members
  - Track shopping progress

- 🥫 **Pantry Inventory**
  - Track items in your pantry
  - Monitor expiry dates
  - Get low stock alerts
  - Auto-update when shopping is completed

## Tech Stack

### Backend
- FastAPI (Python 3.12)
- PostgreSQL 15
- SQLAlchemy ORM
- Pydantic for data validation

### Frontend
- React 19
- Vite
- Tailwind CSS
- Axios for API communication

### Infrastructure
- Docker + Docker Compose
- GitHub Actions (coming soon)

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SmartCart
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. Access the applications:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Setup

### Backend (Local)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend (Local)

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Project Structure

```
SmartCart/
├── backend/
│   ├── app/
│   │   ├── crud.py          # Database operations
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.jsx         
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `DB_HOST`: Database hostname
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

### Frontend
- Environment variables are built into the application at build time

## API Documentation

The API documentation is available at http://localhost:8000/docs when running the application. It includes:
- All available endpoints
- Request/response schemas
- Authentication requirements (coming soon)
- Interactive testing interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)