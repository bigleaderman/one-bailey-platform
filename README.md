# Onebailey FastAPI Project

## Overview
Onebailey is a web application that provides predictions on the US stock market, specifically focusing on whether the market is expected to rise or fall on a given day. The application also offers insights into the Nasdaq QQQ predictions, along with reasons for the predictions.

## Project Structure
The project is organized into the following directories and files:

```
onebailey-fastapi
├── backend
│   ├── app
│   │   ├── main.py               # Entry point of the FastAPI application
│   │   ├── db.py                 # Database connection and configuration
│   │   ├── models.py              # SQLAlchemy models for database tables
│   │   ├── schemas.py             # Pydantic models for data validation
│   │   ├── crud.py                # CRUD operations for predictions
│   │   ├── routers
│   │   │   └── predictions.py     # API routes related to predictions
│   │   ├── services
│   │   │   └── prediction_service.py # Business logic for predictions
│   │   └── templates
│   │       └── index.html         # HTML template for the main page
│   ├── requirements.txt           # Backend dependencies
│   └── Dockerfile                 # Docker instructions for the backend
├── frontend
│   ├── index.html                 # Main HTML file for the frontend
│   ├── app.js                     # JavaScript for frontend logic
│   └── styles.css                 # CSS styles for the frontend
├── tests
│   └── test_predictions.py        # Unit tests for prediction functionality
├── .env.example                   # Example environment variables
├── pyproject.toml                 # Project configuration file
└── README.md                      # Project documentation
```

## Setup Instructions

### Prerequisites
- Python 3.13.9
- PostgreSQL database
- Docker (optional, for containerization)

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd onebailey-fastapi
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install backend dependencies:
   ```
   pip install -r backend/requirements.txt
   ```

4. Configure the database connection in the `.env` file based on the `.env.example`.

### Running the Application
1. Start the backend server:
   ```
   cd backend
   uvicorn app.main:app --reload
   ```

2. Open a new terminal and start the frontend server (if applicable):
   ```
   cd frontend
   # Use a simple HTTP server or any frontend framework to serve the index.html
   ```

3. Access the application in your web browser at `http://localhost:8000`.

## Usage
- The main page displays "Onebailey" in the top left corner.
- It shows whether the US stock market is expected to rise today along with reasons.
- Below that, predictions for the Nasdaq QQQ are displayed.
- A disclaimer about investment loss responsibility and copyright is included at the bottom of the page.

## Disclaimer
This application does not provide financial advice and is not responsible for any investment losses. Please consult with a financial advisor before making investment decisions.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.