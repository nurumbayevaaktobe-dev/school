# Installation Guide - AI ClassGuard Pro v2.0

## Quick Setup (Automated)

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## Manual Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis (optional, for production)
- Platform-specific dependencies (see below)

### 1. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 3. Agent Setup (Student Computers)

```bash
cd agent
pip install -r requirements.txt
```

#### Platform-Specific Agent Dependencies

**Windows:**
```bash
pip install pywin32==306 pygetwindow==0.0.9
```

**macOS:**
```bash
pip install pyobjc-framework-Cocoa==10.1 pyobjc-framework-Quartz==10.1
```

**Linux (Ubuntu/Debian):**
```bash
# Install system packages
sudo apt-get install python3-tk scrot xdotool

# Install Python packages
pip install python-xlib==0.33
```

**Linux (RedHat/CentOS):**
```bash
# Install system packages
sudo yum install python3-tkinter scrot

# Install Python packages
pip install python-xlib==0.33
```

### 4. Configuration

**Backend (.env):**
```bash
cp .env.example .env
nano .env
```

Required environment variables:
- `GEMINI_API_KEY` - Get from https://ai.google.dev/
- `SECRET_KEY` - Random string for Flask sessions
- `JWT_SECRET_KEY` - Random string for JWT tokens

**Frontend (.env):**
```bash
cd frontend
cp .env.example .env
```

**Agent (.env):**
```bash
cd agent
cp .env.example .env
```

Update:
- `SERVER_URL` - URL of backend server (e.g., http://localhost:5000)
- `STUDENT_NAME` - Name of student

### 5. Run the Application

**Start Backend:**
```bash
source venv/bin/activate
python backend/app.py
```

**Start Frontend (new terminal):**
```bash
cd frontend
npm run dev
```

**Start Agent on Student Computers:**
```bash
cd agent
python core/agent.py
```

**Access Dashboard:**
- Open browser to http://localhost:3000

## Troubleshooting

### tkinter not found

**Linux:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
# Should be included with Python from python.org
# If using Homebrew Python:
brew install python-tk
```

**Windows:**
- Reinstall Python from python.org with "tcl/tk and IDLE" option checked

### Screenshot capture fails

**Windows:**
- Install: `pip install mss pillow pywin32`

**macOS:**
- Grant screen recording permissions in System Preferences > Security & Privacy

**Linux:**
- Install scrot or imagemagick: `sudo apt-get install scrot`

### ImportError: pyobjc modules

**macOS:**
```bash
pip install --upgrade pip
pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz
```

### Network connection fails

- Check firewall settings
- Ensure backend is running on correct port
- Update `SERVER_URL` in agent/.env

## Production Deployment

See [Docker deployment guide](docker/README.md) for containerized deployment.

## Getting Help

- Check logs in backend console
- Check browser console for frontend errors
- Check agent console for connection issues
- Open issue on GitHub
