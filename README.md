# 1. Algorithmic Trading Adventure

## Requirements

* Python **3.9 or higher**
* Internet connection (to fetch stock data)

### Python Libraries Used

* `yfinance`
* `pandas`
* `numpy`

---

## Step 1: Create and Activate Virtual Environment

### Create virtual environment

```
py -m venv venv
```

### Activate it

**Windows**

```
venv\Scripts\activate
```

**Mac / Linux**

```
source venv/bin/activate
```

You should see `(venv)` in your terminal.

---

## Step 2: Install Dependencies

```
pip install yfinance pandas numpy
```

---

## Step 3: Run the Project

From the project root directory:

```
py main.py
```

---

## Sample Output

```
--- Trading Performance ---
Initial Budget: 5000
Final Cash: 7421.35
Net Profit: 2421.35
Return (%): 48.43
Total Trades: 6

--- Trade Log ---
('BUY', '2019-04-02', 191.24, 26)
('SELL', '2020-03-23', 224.37, 26)
...
```
## Customization

You can modify the following in `main.py`:

```python
strategy = MovingAverageStrategy(
    symbol="AAPL",
    start_date="2018-01-01",
    end_date="2023-12-31",
    budget=5000
)
```

Change:

* Stock symbol (e.g., `MSFT`, `GOOGL`)
* Date range
* Budget amount


# 2. Samsung Phone Advisor

### Step 1: Prerequisites
You need to have installed on your computer:
- **Python 3.9+**
- **PostgreSQL**

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Wait for all packages to install (this takes 1-2 minutes).

### Step 5: Create the Database
```bash
createdb -U postgres samsung_advisor
```

### Step 6: Set Up API Key
The project uses **Groq API** (completely free). Get a key in 30 seconds:

1. Go to [console.groq.com](https://console.groq.com)
2. Copy your API key
3. Or for this time being you can use my groq api key which is given below just copy paste the whole .env file.
4. Create/edit `.env` file in the project folder and add:
   ```
   GROQ_API_KEY= <your groq api key>
   LLM_MODEL=llama-3.3-70b-versatile
   DATABASE_URL=postgresql://postgres:<your postgresql admin password>@localhost:5432/samsung_advisor
   ```

### Step 7: Run the Application
```bash
python main.py
```

**You'll see something like:**
```
INFO - Database initialized
INFO - Database is empty. Starting automatic scraping...
INFO - This may take 3-5 minutes. Please wait...
[... scraping phones ...]
INFO - Scraping completed successfully! Added 30 Samsung phones to database
INFO - System ready to answer questions!
```

### Step 8: Open in Browser
Once you see "System ready", open:
- **Chat Interface**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs

**Done! ** Start asking questions about Samsung phones!

