
# Sentiment E-commerce Application

An AI-powered e-commerce platform that leverages advanced sentiment analysis to transform product reviews into actionable insights for shoppers and businesses.

## Key Technologies

- Python backend with AI sentiment analysis
- SQLAlchemy for database management
- NLTK for natural language processing
- Machine learning-powered review processing
- Interactive user interface with sentiment visualization

## Local Setup Instructions

### Prerequisites

1. Python 3.9 or higher
2. PostgreSQL database
3. Git



##  Local Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/shitalv/SentimentEcommerce.git
cd SentimentEcommerce
```


### 2. Update Code Files

Update `app.py` and `init_db.py` with the latest code provided. These updates will:
- Ensure the app always uses your local PostgreSQL database
- Improve database connection handling
- Add enhanced logging to help debug issues

### 3. Set Up a Python Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

# Activate it
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install flask flask-cors flask-login flask-sqlalchemy flask-wtf gunicorn nltk psycopg2-binary email-validator
```


### 5. Download NLTK Data


```bash
python -c "import nltk; nltk.download('vader_lexicon')"
```

### Step 5: Set Up PostgreSQL Database

1. Create a new database in PostgreSQL:
   ```sql
   CREATE DATABASE sentiment_ecommerce;
   ```

2. The application is configured to use local PostgreSQL with these default settings:
   - Host: localhost
   - Port: 5432
   - Database: sentiment_ecommerce
   - Username: postgres
   - Password: postgres

3. If your PostgreSQL setup uses different credentials, you can set the `DATABASE_URL` environment variable:
   ```
   # Windows
   set DATABASE_URL=postgresql://your_username:your_password@localhost:5432/sentiment_ecommerce
   
   # macOS/Linux
   export DATABASE_URL=postgresql://your_username:your_password@localhost:5432/sentiment_ecommerce
   ```

### 6. Create a PostgreSQL Database

Open your PostgreSQL client and run:

```sql
CREATE DATABASE sentiment_ecommerce;
```

### 7. Initialize the Database

```bash
python init_db.py
```


### Step 7: Run the Application

### 8. Run the Application


```bash
python main.py
```


### Step 8: Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## Features

- Sentiment analysis of product reviews
- User authentication system
- Visual representation of sentiment through charts
- "Hype vs Reality" analysis comparing marketing claims to user experiences
- Search and filtering by product name, category, and sentiment

## Troubleshooting

If you encounter database connection issues:
1. Verify PostgreSQL is running
2. Check that your database credentials are correct
3. Ensure the database exists and your user has proper permissions

### 9. Access the Application

Open your browser and visit:

[http://localhost:5000](http://localhost:5000)
