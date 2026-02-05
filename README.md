# Algorithmic Trading Adventure

## 🛠 Requirements

* Python **3.9 or higher**
* Internet connection (to fetch stock data)

### Python Libraries Used

* `yfinance`
* `pandas`
* `numpy`

---

## ⚙️ Step 1: Create and Activate Virtual Environment

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

## 📦 Step 2: Install Dependencies

```
pip install yfinance pandas numpy
```

---

## ▶️ Step 3: Run the Project

From the project root directory:

```
py main.py
```

---

## 🧾 Sample Output

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
## 🚀 Customization

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

```
