from trading_strategy import MovingAverageStrategy

strategy = MovingAverageStrategy("AAPL", "2018-01-01", "2023-12-31", 5000)

strategy.fetch_data()
# print(strategy.data.head())
strategy.clean_data()
strategy.calculate_indicators()
strategy.generate_signals()
strategy.execute_trades()
strategy.close_final_position()

results = strategy.calculate_performance()

print("\n--- Trading Performance ---")
for key, value in results.items():
    print(f"{key}: {value}")

print("\n--- Trade Log ---")
for trade in strategy.trades:
    print(trade)