# SmartCart

A smart grocery planning and budget management application that helps households manage their shopping lists, pantry inventory, and track household members. Designed for iOS/Safari with full mobile optimization.

🔗 **Live Demo**: https://ericsSandbox.github.io/smartcart/

## Features

- 🏠 **Household Management**
  - Add and manage household members
  - Track allergies and dietary preferences
  - View member profiles

- 📝 **Shopping Lists**
  - Create shopping lists with items
  - Mark items as completed
  - Real-time search and filtering
  - Persistent data storage

- 🥫 **Pantry Inventory**
  - Track items in your pantry
  - Monitor expiry dates with visual alerts
  - Get low stock warnings
  - Search and filter inventory
  - Adjust quantities easily

- 📱 **Barcode Scanner** (Beta)
  - Real-time barcode detection using device camera
  - Automatic product lookup from Open Food Facts database
  - Manual entry fallback for unrecognized barcodes
  - Debug logging for troubleshooting

## Tech Stack

### Frontend (Deployed to GitHub Pages)
- HTML5 + CSS3 + Vanilla JavaScript (No frameworks)
- Canvas API for barcode detection
- MediaDevices API for camera access
- localStorage for persistent data
- jsQR + Tesseract.js for barcode decoding
- Responsive design optimized for iOS Safari

### Backend (Optional)
- FastAPI (Python 3.12)
- PostgreSQL 15
- Docker + Docker Compose (not currently deployed)

## Prerequisites

- **To Use**: Modern mobile browser (iOS Safari, Android Chrome) or desktop browser
- **To Develop Locally**: Node.js 20+ (for frontend) or Python 3.12+ (for backend)

## Quick Start - Using the Live App

Simply visit **https://ericsSandbox.github.io/smartcart/** on any device with a modern browser. Your data is stored locally on your device using browser localStorage.

### Supported Browsers
- ✅ iOS Safari (primary target)
- ✅ Chrome/Chromium on desktop and Android
- ✅ Firefox on desktop
- ✅ Any modern browser with localStorage support

## Installation for Local Development

### GitHub Pages Deployment (Automatic)

The application automatically deploys to GitHub Pages on every push to `main`. To set up:

1. Fork or clone this repository
2. Enable GitHub Pages in repository settings:
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: main
   - Folder: / (root)
3. Your app will be live at `https://<your-username>.github.io/smartcart/`

The deployment is fully automated via `.github/workflows/deploy.yml`.

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/ericsSandbox/smartcart.git
   cd SmartCart
   ```

2. Simply open `index.html` in your browser:
   ```bash
   # Linux/macOS
   open index.html
   
   # Or with Python's simple server
   python -m http.server 8000
   # Then visit http://localhost:8000
   ```

3. Or use Docker Compose (if running the full stack):
   ```bash
   docker-compose up -d
   ```
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## Usage Guide

### Pantry Tab
- **Add Items**: Click "+" button to add items manually or use barcode scanner
- **View Items**: All pantry items displayed with quantity, unit, and expiry status
- **Manage Stock**: Use +/- buttons to adjust quantities
- **Expiry Alerts**: Red background indicates expired items, yellow indicates expiring soon
- **Search**: Use search box to filter items by name

### Shopping List Tab
- **Create Lists**: Add shopping list items
- **Mark Complete**: Click checkbox to mark items as done (strikethrough)
- **Search**: Filter shopping items by name

### Members Tab
- **Add Members**: Click "+" to add household members
- **Track Info**: Record age, allergies, and dietary preferences
- **View Profiles**: See all member information in one place

### Barcode Scanner Tab (Beta)
- **Select Camera**: Choose which camera to use (front/rear)
- **Scan**: Point camera at barcode
- **Auto-Lookup**: Automatically looks up product info from Open Food Facts
- **Manual Entry**: If barcode not found in database, manually enter product name
- **Debug**: View real-time detection logs for troubleshooting

### Settings Tab
- **Clear Data**: Delete all stored data (pantry, shopping lists, members)
- **Export Data**: View stored data as JSON for backup
- **Storage Info**: See how much data is stored locally

## Data Storage

All data is stored locally in your browser's localStorage. This means:
- ✅ No data sent to any server (privacy-friendly)
- ✅ Data persists between sessions
- ❌ Data is device-specific (not synced across devices)
- ❌ Clearing browser data will delete your items

**Backup Recommendation**: Periodically export your data from Settings tab

## Project Structure

```
SmartCart/
├── index.html               # Main application (single-file app)
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Pages deployment
├── .nojekyll                # GitHub Pages configuration
├── backend/                 # Optional Python backend
│   ├── app/
│   │   ├── crud.py         # Database operations
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # SQLAlchemy models
│   │   └── schemas.py      # Pydantic schemas
│   └── requirements.txt
├── frontend/                # Optional React frontend
│   ├── src/
│   ├── package.json
│   └── README.md
├── docker-compose.yml
└── README.md
```

## Known Issues & Limitations

### Barcode Scanner (Beta)
- **Detection**: Works well with clear, standard barcodes
- **Decoding**: Currently uses manual entry as primary method (jsQR/Tesseract not fully reliable)
- **Recommendation**: Use manual entry for consistent results
- **Debug**: Check scanner logs if detection isn't working

### Data Limitations
- ❌ No multi-device sync (data is device-specific)
- ❌ No cloud backup (export manually from Settings)
- ❌ No sharing with other users (planned feature)

### Browser Limitations
- Requires modern browser with localStorage support
- iOS Safari: May need permission to access camera for barcode scanner
- Private/Incognito mode: Data may not persist (depends on browser settings)