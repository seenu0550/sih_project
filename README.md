# Smart Classroom & Timetable Scheduler

A comprehensive web-based platform for efficient class scheduling in higher education institutions. Built with FastAPI backend, React.js frontend, and MongoDB database.

## Features

- **User Authentication**: Secure login and registration system
- **Classroom Management**: Manage classrooms with capacity and equipment details
- **Subject Management**: Define subjects with credit hours and class requirements
- **Faculty Management**: Track faculty availability and subject expertise
- **Batch Management**: Organize student batches by department and semester
- **Intelligent Scheduling**: Generate multiple optimized timetable options using OR-Tools
- **Workflow Management**: Review and approve timetables with status tracking
- **Responsive UI**: Modern Material-UI based interface

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database with Motor async driver
- **OR-Tools**: Google's optimization library for scheduling
- **JWT Authentication**: Secure token-based authentication
- **Pydantic**: Data validation and serialization

### Frontend
- **React.js**: Modern JavaScript library
- **Material-UI**: React component library
- **Axios**: HTTP client for API requests
- **React Router**: Client-side routing

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- MongoDB 4.4+

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Update .env file with your MongoDB connection string
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=timetable_scheduler
SECRET_KEY=your-secret-key-here
```

5. Start the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Setup Data**: Add classrooms, subjects, faculty, and student batches
3. **Generate Timetable**: Use the timetable generator with your requirements
4. **Review Options**: Choose from multiple generated timetable options
5. **Approve**: Review and approve the final timetable

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Key Parameters for Timetable Generation

- Number of classrooms and their capacities
- Subject details with classes per week
- Faculty availability and subject expertise
- Student batch sizes and subject requirements
- Working days and time slots
- Maximum classes per day constraints

## Project Structure

```
sih-2025-1/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # MongoDB connection
│   ├── auth.py              # Authentication utilities
│   ├── scheduler.py         # Timetable scheduling logic
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── context/         # React context
│   │   ├── services/        # API services
│   │   └── App.js           # Main App component
│   ├── package.json         # Node dependencies
│   └── public/              # Static files
└── README.md                # Project documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.