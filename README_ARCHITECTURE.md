# Hombres Lobo - Separated Architecture

This project has been restructured to properly separate the backend API from the Vue.js frontend.

## Architecture

### Backend (FastAPI)
- **Location**: `/app/` directory 
- **Technology**: FastAPI with Python
- **Purpose**: RESTful API for game logic, user management, and data persistence
- **Port**: 8000 (development)

### Frontend (Vue.js)
- **Location**: `/frontend/` directory
- **Technology**: Vue 3 with Vite
- **Purpose**: User interface for the Hombres Lobo game
- **Port**: 5173 (development)

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: http://localhost:5173

## Key Changes Made

1. **Backend Cleanup**:
   - Removed static file serving from FastAPI
   - Removed Jinja2 template rendering
   - Added CORS middleware for frontend communication
   - Pure API-only backend

2. **Frontend Creation**:
   - New Vue.js 3 application with Vite
   - API service layer for backend communication
   - Responsive design for mobile devices
   - Authentication handling with JWT tokens

3. **Communication**:
   - Frontend communicates with backend via REST API
   - CORS configured for development (ports 3000, 8080, 5173)
   - Token-based authentication

## API Endpoints

The backend provides RESTful endpoints for:
- User registration and authentication
- Game creation and management
- Player actions (voting, special abilities)
- Game state management

See the FastAPI documentation at http://localhost:8000/docs for complete endpoint details.

## Production Deployment

For production:
1. Build the frontend: `cd frontend && npm run build`
2. Serve the frontend build files through a web server (nginx, Apache)
3. Configure the backend to run with a production WSGI server
4. Update CORS settings for production domain
5. Set up proper environment variables

## Testing

Backend tests can be run with:
```bash
python -m pytest tests/ -v
```

All 182 existing tests continue to pass, ensuring backend functionality is preserved.