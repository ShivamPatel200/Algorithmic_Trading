# Developer: Shivam Patel
# Created on 12/26/21
# Algorithmic Trading Using Python - Full Course by https://github.com/nickmccullum/algorithmic-trading-python

# Goal: create a Python script that will accept the value of your portfolio and tell you how many shares of each S&P 500 constituent you should purchase to get an equal-weight version of the index fund

# import libraries / third-party dependency
import pandas as pd # data science library
import requests # allows for HTTP requests
import math # Access to math functions

# import a list of stocks
stocks = pd.read_csv('sp_500_stocks.csv')

# import IEX Cloud API token
API_Token = open("API_Token.txt", "r").readline().strip()

# Make an API call - Example
symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={API_Token}'
data = requests.get(api_url).json()

# Parse the API call - Example
price = data["latestPrice"]
market_cap = data["marketCap"]

# Add stock data to a pd DataFrame - Example
cols = ["Ticker", "Stock Price", "Market Capitilization", "Number of Shares to Buy"]
final_dataframe = pd.DataFrame(columns=cols)
final_dataframe = final_dataframe.append(
    pd.Series(
    [
        symbol,
        price,
        market_cap,
        "N/A"
    ],
    index = cols
    ),
    ignore_index=True
)

# Looping through the tickers in our list of stocks - Too Slow
#final_dataframe = pd.DataFrame(columns=cols)
#for stock in stocks['Ticker']:
#    api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={API_Token}'
#    data = requests.get(api_url).json()
#    final_dataframe = final_dataframe.append(
#        pd.Series(
#            [
#                stock,
#                data["latestPrice"],
#                data["marketCap"],
#                "N/A"
#            ],
#            index=cols
#        ),
#        ignore_index=True
#    )


# Use Batch API Calls to improve performance
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

final_dataframe = pd.DataFrame(columns=cols)
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={API_Token}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(","):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']['latestPrice'],
                    data[symbol]['quote']['marketCap'],
                    "N/A"
                ], index=cols
                ),
            ignore_index=True
        )

# Calculate the number of shares to buy
portfolio_size = input('Enter the value of your portfolio: ')
try:
    val = float(portfolio_size)
except ValueError:
    print("That's not a number \nPlease try again")
    portfolio_size = input('Enter the value of your portfolio: ')
    val = float(portfolio_size)

position_size = val/len(final_dataframe.index)
for i in range(0, len(final_dataframe)):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/final_dataframe.loc[i, 'Stock Price'])

pd.set_option("display.max_rows", None, "display.max_columns", None)

# Final Results
print(final_dataframe)