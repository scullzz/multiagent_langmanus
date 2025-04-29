import pandas as pd
import numpy as np
import yfinance as yf

def calculate_average_annual_return(ticker, years=5):
    """
    Calculate the average annual return for a given ticker over a specified number of years.
    
    Parameters:
    ticker (str): The ticker symbol
    years (int): Number of years to look back
    
    Returns:
    float: Average annual return as a percentage
    """
    # Calculate start and end dates using pandas
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(years=years)
    
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    print(f"Calculating average annual return for {ticker} from {start_date_str} to {end_date_str}")
    
    # Download the data
    data = yf.download(ticker, start=start_date_str, end=end_date_str, progress=False)
    
    if data.empty:
        return f"No data found for ticker {ticker} in the specified date range."
    
    # Calculate the total return
    initial_price = data['Close'].iloc[0]
    final_price = data['Close'].iloc[-1]
    total_return = (final_price - initial_price) / initial_price
    
    # Calculate the number of years (actual)
    start_datetime = data.index[0]
    end_datetime = data.index[-1]
    actual_years = (end_datetime - start_datetime).days / 365.25
    
    # Calculate the average annual return using CAGR formula
    cagr = ((1 + total_return) ** (1 / actual_years)) - 1
    
    print(f"Initial price: ${initial_price:.2f}")
    print(f"Final price: ${final_price:.2f}")
    print(f"Total return: {total_return*100:.2f}%")
    print(f"Time period: {actual_years:.2f} years")
    
    return cagr * 100  # Convert to percentage

if __name__ == "__main__":
    # Example usage
    print("Calculating returns for SPY (S&P 500 ETF)...")
    spy_return = calculate_average_annual_return('SPY', years=5)
    print(f"Average annual return for SPY over the last 5 years: {spy_return:.2f}%")
    
    # Calculate for a few other popular assets
    tickers = ['AAPL', 'MSFT', 'AMZN']
    for ticker in tickers:
        try:
            annual_return = calculate_average_annual_return(ticker, years=5)
            print(f"Average annual return for {ticker} over the last 5 years: {annual_return:.2f}%")
        except Exception as e:
            print(f"Error calculating return for {ticker}: {e}")
    
    # Calculate for a longer time period
    spy_10yr_return = calculate_average_annual_return('SPY', years=10)
    print(f"\nAverage annual return for SPY over the last 10 years: {spy_10yr_return:.2f}%")
    
    # Calculate for a market index
    print("\nCalculating returns for ^GSPC (S&P 500 Index)...")
    sp500_return = calculate_average_annual_return('^GSPC', years=5)
    print(f"Average annual return for S&P 500 Index over the last 5 years: {sp500_return:.2f}%")
