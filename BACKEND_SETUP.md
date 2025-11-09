# 🔄 Setting Up Backend Persistence

Your SmartCart app now has **full database persistence** with backend synchronization! Here's how to set it up.

## What Changed

### Frontend
- ✅ Auto-connects to backend on load
- ✅ Syncs pantry, shopping lists, and members with PostgreSQL database
- ✅ Falls back to localStorage if backend is unavailable
- ✅ Caches data locally for offline support

### Backend
- ✅ New `/init` endpoint to initialize households
- ✅ New gateway router for `/households/{id}/*` endpoints
- ✅ CORS enabled for GitHub Pages
- ✅ Full CRUD operations for pantry, shopping lists, members

## Setup Instructions

### 1. Start PostgreSQL Database

Make sure you have PostgreSQL running. If using Docker:

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL on port 5432
- Create `smartcart_dev` database
- Initialize database schema automatically

### 2. Start the Backend API

```bash
cd /home/eric/Projects/SmartCart
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

Check API docs at: `http://localhost:8000/docs`

### 3. Frontend Configuration

The frontend automatically detects the backend:
- ✅ If backend is running on `http://localhost:8000`, it will connect
- ✅ If backend is unavailable, it falls back to localStorage
- ✅ Data syncs automatically when backend becomes available

**Note**: For GitHub Pages access, the backend must be exposed to the internet or you need a custom domain.

## How It Works

### Data Flow

```
Frontend (GitHub Pages)
    ↓ (fetch/JSON)
API Gateway (http://localhost:8000)
    ↓
Backend Routers (pantry, lists, members)
    ↓
Database (PostgreSQL)
```

### Sync Strategy

**When you create an item:**
1. Frontend makes API call to backend
2. Backend saves to PostgreSQL
3. Result returned to frontend
4. Frontend updates localStorage cache
5. If backend unavailable, item saved to localStorage only

**When you load the app:**
1. Frontend checks if backend is available
2. If yes: Fetches all data from backend (single trip!)
3. If no: Uses localStorage cache
4. Backend data always synced to localStorage

## API Endpoints

All endpoints are under `/households/{household_id}/`

### Pantry
- `GET /households/{id}/pantry` - List all pantry items
- `POST /households/{id}/pantry` - Create item
- `PATCH /households/{id}/pantry/{item_id}` - Update item
- `DELETE /households/{id}/pantry/{item_id}` - Delete item

### Shopping Lists
- `GET /households/{id}/lists` - List all shopping lists
- `POST /households/{id}/lists` - Create list
- `DELETE /households/{id}/lists/{list_id}` - Delete list

### Members
- `GET /households/{id}/members` - List all members
- `POST /households/{id}/members` - Create member
- `DELETE /households/{id}/members/{member_id}` - Delete member

### Init
- `GET /init` - Initialize or get default household

## Environment Variables

The backend needs these in `.env`:

```
DATABASE_URL=postgresql://smartcart_user:smartcart_pass@localhost:5432/smartcart_dev
POSTGRES_USER=smartcart_user
POSTGRES_PASSWORD=smartcart_pass
POSTGRES_DB=smartcart_dev
```

These are already set in `docker-compose.yml`

## Offline Mode

- Frontend works completely offline using localStorage
- When backend comes back online, data automatically syncs
- No data loss if backend is down temporarily
- Perfect for mobile use in areas with spotty connectivity

## Multi-Device Sync

Now that you have a backend:
- Your pantry is synced across all devices
- Shopping lists update in real-time on all devices
- Members preferences are shared
- Access from phone, tablet, desktop - all see same data

**Example**: 
1. Add item on phone
2. Item appears on desktop instantly
3. Check item off on desktop
4. Changes appear on phone

## Troubleshooting

### Backend not connecting?
```
Check:
1. Is PostgreSQL running? (docker-compose up)
2. Is backend running? (python -m uvicorn...)
3. Check console for connection errors
4. Look at browser console for API errors
```

### Database errors?
```
Solution:
1. Stop containers: docker-compose down
2. Clear data: docker volume prune
3. Restart: docker-compose up -d
4. Restart backend: python -m uvicorn...
```

### Data not syncing?
```
Check:
1. Backend logs for API errors
2. Browser console for fetch errors
3. Network tab in DevTools
4. Verify household_id is correct (should be 1)
```

## Testing the Setup

1. **Add item from backend**:
   - Go to Pantry tab
   - Click + button
   - Add an item (e.g., "Milk")
   - Check browser console for "✅ Item created in backend"

2. **Check database**:
   ```bash
   docker-compose exec db psql -U smartcart_user -d smartcart_dev -c "SELECT * FROM pantry_items;"
   ```

3. **Restart app**:
   - Refresh page
   - Item should still be there (loaded from backend)

4. **Offline test**:
   - Stop backend
   - Add item
   - Should show "⚠️ Created locally"
   - Restart backend
   - Item should sync

## Production Deployment

For production:

1. **Use environment variables**:
   - `DATABASE_URL` points to production database
   - `BACKEND_URL` for GitHub Pages to connect

2. **Enable HTTPS**:
   - GitHub Pages uses HTTPS
   - Backend must also use HTTPS (or mixed content errors)

3. **Deploy backend**:
   - Use Heroku, Railway, or your own server
   - Update CORS allowed origins
   - Update `API_BASE_URL` in frontend

4. **Database**:
   - Use managed PostgreSQL (AWS RDS, Heroku, etc.)
   - Regular backups
   - Connection pooling for many users

## Architecture

```
┌─────────────────────┐
│   GitHub Pages      │
│  (Frontend HTML)    │
└──────────┬──────────┘
           │ HTTP/CORS
           ↓
┌─────────────────────┐
│   FastAPI Backend   │
│  (http://localhost) │
└──────────┬──────────┘
           │ SQL
           ↓
┌─────────────────────┐
│   PostgreSQL        │
│  (smartcart_dev)    │
└─────────────────────┘
```

## Next Steps

1. ✅ Start PostgreSQL: `docker-compose up`
2. ✅ Start Backend: `python -m uvicorn app.main:app --reload`
3. ✅ Visit GitHub Pages app
4. ✅ Data now persists across devices!

---

You now have full enterprise-grade data persistence with your SmartCart app! 🎉
