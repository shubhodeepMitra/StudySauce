# StudySauce - AI-Powered Learning Platform

StudySauce is an innovative learning platform that combines AI-powered video generation with personalized learning paths. It helps students assess their current understanding of K12 subjects and provides a customized learning roadmap with AI tutor videos.

## Features

- Initial assessment to determine current knowledge level
- Personalized learning roadmap
- AI tutor videos using Tavus API
- Progress tracking and checkpoints
- Support for multiple K12 subjects

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- Tavus API key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/studysauce.git
cd studysauce
```

2. Install frontend dependencies:
```bash
npm install
```

3. Set up the Python backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your Tavus API key:
```
VITE_APP_TAVUS_API_KEY=your_api_key_here
```

## Running the Application

1. Start the backend server:
```bash
cd backend
python run.py
```

2. In a new terminal, start the frontend development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
studysauce/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── requirements.txt
│   └── run.py
├── src/
│   ├── components/
│   │   ├── Assessment/
│   │   ├── Learning/
│   │   └── Tutor/
│   └── App.tsx
├── package.json
└── README.md
```

## API Endpoints

### Assessment
- `POST /api/assessment/create` - Create a new assessment
- `POST /api/assessment/{id}/level` - Update student's current level
- `POST /api/assessment/{id}/checkpoint` - Add a new checkpoint
- `GET /api/assessment/{id}/roadmap` - Get learning roadmap

### Video Generation
- `POST /api/video/create` - Create a new video
- `GET /api/video/{id}/status` - Get video generation status
- `GET /api/avatars` - Get available avatars

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
