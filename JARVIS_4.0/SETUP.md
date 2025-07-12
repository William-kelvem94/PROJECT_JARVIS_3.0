# 🚀 JARVIS 4.0 - Setup & Usage Guide

## 🎯 Quick Start

### Option 1: Docker Compose (Recommended)
```bash
cd JARVIS_4.0
docker-compose up --build
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd JARVIS_4.0/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd JARVIS_4.0/frontend
npm install
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## 🔐 Default Credentials

- **Username**: `admin`
- **Password**: `jarvis123`

## 🏗️ Architecture Overview

```
JARVIS_4.0/
├── 🌐 frontend/          # React 18 + TypeScript + Vite
│   ├── src/components/   # Reusable UI components
│   ├── src/modules/      # Feature modules (auth, chat, voice, vision)
│   ├── src/stores/       # Zustand state management
│   └── src/styles/       # Glassmorphism design system
├── 🧠 backend/           # FastAPI + AsyncIO
│   ├── api/routes/       # REST API endpoints
│   ├── core/             # Core system (config, database, AI manager)
│   ├── modules/          # AI modules (chat, voice, vision)
│   └── models/           # Database models
├── 🐳 docker/            # Container configuration
└── 📚 docs/              # Documentation
```

## 🎨 Features Implemented

### ✅ Core Infrastructure
- **FastAPI** backend with async support
- **React 18** frontend with TypeScript
- **Glassmorphism UI** with theme switching
- **JWT Authentication** with secure sessions
- **SQLite Database** with async operations
- **WebSocket** support for real-time communication

### ✅ Authentication System
- JWT-based login/logout
- Session management
- Protected routes
- User management

### ✅ Modern UI/UX
- **Glassmorphism** design language
- **Theme System**: Dark, Light, Neon, Matrix
- **Responsive Design** for all devices
- **Smooth Animations** with Framer Motion
- **Loading States** and transitions

### ✅ API Architecture
- **RESTful endpoints** for all features
- **OpenAPI documentation** (Swagger UI)
- **Health monitoring** endpoints
- **Error handling** and validation

## 🔧 AI Modules (Ready for Integration)

### Chat Module
- **Framework**: Ready for Ollama integration
- **Endpoint**: `POST /api/chat/message`
- **Features**: Conversation history, context management

### Voice Module  
- **Framework**: Ready for Whisper + TTS
- **Endpoints**: 
  - `POST /api/voice/transcribe` (Speech-to-Text)
  - `POST /api/voice/speak` (Text-to-Speech)
  - `POST /api/voice/process` (Full voice pipeline)

### Vision Module
- **Framework**: Ready for YOLO + OpenCV
- **Endpoints**:
  - `POST /api/vision/detect` (Object detection)
  - `POST /api/vision/classify` (Image classification)
  - `POST /api/vision/faces` (Face detection)

## 📊 System Monitoring

### Health Endpoints
- `GET /health` - Basic health check
- `GET /api/system/health` - Comprehensive health status
- `GET /api/system/status` - System metrics
- `GET /api/system/metrics` - Detailed performance metrics

### Status Monitoring
- AI module availability
- Database connection status
- WebSocket connection status
- Model loading status

## 🛠️ Development Workflow

### Backend Development
```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Check API docs
open http://localhost:8000/api/docs
```

### Frontend Development
```bash
cd frontend
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐳 Docker Setup

### Development
```bash
# Start all services
docker-compose up --build

# Start specific service
docker-compose up backend
docker-compose up frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Production
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🔮 Next Steps for Full AI Integration

### 1. Install Ollama (Local LLM)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama service
ollama serve
```

### 2. Install Whisper (Speech-to-Text)
```bash
pip install openai-whisper
```

### 3. Install Computer Vision
```bash
pip install opencv-python ultralytics
```

### 4. Enable Full Functionality
Once AI dependencies are installed, restart the backend to enable full functionality:
```bash
uvicorn main:app --reload
```

## 🎭 Theme System

### Available Themes
- **Dark** (default) - Professional dark theme
- **Light** - Clean light theme  
- **Neon** - Cyberpunk neon theme
- **Matrix** - Green matrix-style theme

### Theme Switching
Themes can be switched via the UI or programmatically:
```typescript
import { useThemeStore } from '@/stores/themeStore'

const { setTheme } = useThemeStore()
setTheme('neon') // Changes to neon theme
```

## 🔒 Security Features

- JWT token authentication
- CORS protection
- Rate limiting ready
- Input validation
- Secure password hashing
- Session management

## 📝 API Usage Examples

### Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "jarvis123"}'

# Get user info
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Chat
```bash
# Send message
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Hello JARVIS", "user_id": "user123"}'
```

### System Status
```bash
# Get system health
curl -X GET http://localhost:8000/api/system/health
```

## 🎯 Ready for Production

The JARVIS 4.0 foundation is complete and ready for:
- AI model integration (Ollama, Whisper, YOLO)
- Advanced chat interfaces
- Voice command processing
- Computer vision capabilities
- Plugin system development
- Mobile app development (React Native)

## 💡 Key Benefits

1. **100% Local** - No external AI dependencies required
2. **Modern Stack** - Latest technologies and best practices
3. **Scalable Architecture** - Modular and extensible design
4. **Beautiful UI** - Professional glassmorphism interface
5. **Developer Friendly** - Excellent DX with hot reload and docs
6. **Production Ready** - Docker, health checks, monitoring