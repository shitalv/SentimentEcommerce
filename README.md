##  Local Setup Instructions

### 1. Clone the Repository

If you haven't already, clone the repository:

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

### 6. Create a PostgreSQL Database

Open your PostgreSQL client and run:

```sql
CREATE DATABASE sentiment_ecommerce;
```

### 7. Initialize the Database

```bash
python init_db.py
```

### 8. Run the Application

```bash
python main.py
```

### 9. Access the Application

Open your browser and visit:

[http://localhost:5000](http://localhost:5000)

