# Nursing School Organizer - Database Setup

## Quick Setup Guide

### 1. Install Python Dependencies
```bash
pip install Flask==2.3.3 Flask-CORS==4.0.0 python-dotenv==1.0.0
```

### 2. Save the Backend Code
Save the Python backend code as `app.py` in your project directory.

### 3. Run the Backend Server
```bash
python app.py
```

The server will start on `http://localhost:5000`

### 4. Update the Frontend
Replace your `template.html` with the updated version that includes database connectivity.

### 5. Open the Frontend
Open `template.html` in your browser. The app will automatically:
- Connect to the database
- Initialize with default St. Clair requirements
- Sync all data across browsers and devices

## Features Added

### Database Benefits:
- **Cross-Browser Persistence**: Data works on any browser, any device
- **Backup/Restore**: Built-in data export functionality  
- **Concurrent Access**: Multiple users can access the same data
- **Data Integrity**: SQL database ensures data consistency
- **Scalability**: Easy to add new features and data types

### API Endpoints:
- `GET/POST /api/assignments` - Manage assignments
- `GET/POST /api/clinical-shifts` - Track clinical hours
- `GET/POST /api/requirements` - Monitor requirements
- `GET/POST /api/goals` - Track goals
- `GET/POST /api/grades` - Record grades
- `GET/POST /api/flashcards` - Study cards
- `GET/POST /api/settings` - App settings
- `GET /api/backup` - Export all data

### File Structure:
```
nursing WebApp/
├── app.py                 # Backend server
├── template.html          # Frontend app
├── nursing_app.db         # SQLite database (auto-created)
├── favicon_io/            # Your favicon files
│   ├── favicon.ico
│   ├── apple-touch-icon.png
│   └── ...
└── README.md
```

## Troubleshooting

### Port Issues
If port 5000 is busy, change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### CORS Issues
The backend includes CORS headers for cross-origin requests.

### Database Location
The SQLite database file `nursing_app.db` will be created in the same directory as `app.py`.

## Usage
1. Start the backend: `python app.py`
2. Open `template.html` in any browser
3. All data automatically syncs to the database
4. Access from multiple browsers/devices using the same backend

Key Features Included:
Dashboard

Progress tracking through the 5-semester program
Upcoming events from both St. Clair dates and personal assignments
Urgent requirements alerts
Current semester selector

Assignment Tracker

Add assignments with due dates, course codes, and weights
Visual status indicators (urgent, pending, completed)
Automatic calculation of days remaining
Course integration with actual St. Clair program structure

Clinical Tracker

Log clinical shifts with hours, locations, and units
Progress tracking against semester requirements
Integration with actual hospital placements (Windsor Regional, Hotel Dieu Grace, etc.)
Visual progress bars for clinical hour completion

Requirements Tracker

Pre-loaded with all Synergy Gateway requirements
Automatic deadline tracking with renewal cycles
Status updates (pending, in-progress, completed, expired)
Math test preparation section for Year 2 requirements

Study Tools

Pomodoro timer with preset intervals
Flashcard system for nursing terminology
Quick notes that auto-save
Study session tracking

Goals Tracker

Academic, clinical, personal, and career goal categories
Progress visualization
Target date tracking with urgency indicators

Technical Features:

Fully responsive design
Local storage (all data saves automatically)
No login required
Clean, professional interface
Mobile-friendly for use during clinical shifts

The app is pre-populated with all the program-specific information from the St. Clair documents, including course codes, clinical requirements, important dates, and Synergy requirements. She can start using it immediately and customize it as needed throughout her program.
The data persists in the browser's local storage, so her information will be saved between sessions. This makes it perfect for personal use while maintaining privacy.

Screenshots
![Dashboard](screenshots/image.png)

![Assignments](screenshots/image-1.png)

![Clinical](screenshots/image-2.png)

![Requirements](screenshots/image-3.png)

![Study](screenshots/image-4.png)

![Goals](screenshots/image-5.png)

