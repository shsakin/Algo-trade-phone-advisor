import yfinance as yf
import pandas as pd

class MovingAverageStrategy:
    def __init__(self, symbol, start_date, end_date, budget=5000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        
        self.data = None
        self.cash = budget
        self.position = 0
        self.trades = []
    
    def fetch_data(self):
        self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date)
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.get_level_values(0)

    def clean_data(self):
        self.data = self.data[~self.data.index.duplicated()]
        self.data = self.data.ffill()


    def calculate_indicators(self):
        self.data["MA50"] = self.data["Close"].rolling(window=50).mean()
        self.data["MA200"] = self.data["Close"].rolling(window=200).mean()

    def generate_signals(self):
        self.data["Signal"] = 0
        self.data.loc[self.data["MA50"] > self.data["MA200"], "Signal"] = 1
        self.data["Position_Change"] = self.data["Signal"].diff()

    def execute_trades(self):
        for date, row in self.data.iterrows():
            price = float(row["Close"])
            signal = row["Position_Change"]

            if pd.isna(signal):
                continue

            # BUY on Golden Cross
            if row["Position_Change"] == 1 and self.position == 0:
                shares = int(self.cash // price)
                if shares > 0:
                    self.position = shares
                    self.cash -= shares * price
                    self.trades.append(("BUY", date.strftime("%Y-%m-%d"), round(price, 2), shares))

            # SELL on Death Cross
            elif row["Position_Change"] == -1 and self.position > 0:
                self.cash += self.position * price
                self.trades.append(("SELL", date.strftime("%Y-%m-%d"), round(price, 2), self.position))
                self.position = 0

    def close_final_position(self):
        if self.position > 0:
            last_price = self.data.iloc[-1]["Close"]
            self.cash += self.position * last_price
            self.trades.append(("FORCE_SELL", self.data.index[-1].strftime("%Y-%m-%d"), round(last_price, 2),self.position))
            self.position = 0

    def calculate_performance(self):
        profit = self.cash - self.budget
        return {
            "Initial Budget": self.budget,
            "Final Cash": round(self.cash, 2),
            "Net Profit": round(profit, 2),
            "Return (%)": round((profit / self.budget) * 100, 2),
            "Total Trades": len(self.trades)
        }