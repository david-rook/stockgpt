import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta
from ta import momentum
import openai
from datetime import datetime, timedelta
from fpdf import FPDF

# Replace your_api_key with your actual OpenAI API key
openai.api_key = ""

# Read stock tickers from file
with open('stock_tickers.txt', 'r') as file:
    tickers = [line.strip() for line in file]

# Calculate the date range for the last year
end_date = datetime.now()
start_date = end_date - timedelta(days=1095)

# Create a PDF to store charts
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Loop through each stock ticker
for ticker in tickers:
    # Get price data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Save price data to CSV
    #data.to_csv(f'{ticker}_price_data.csv')

    # Calculate technical indicators
    data['50_day_MA'] = ta.trend.SMAIndicator(data['Close'], 50).sma_indicator()
    data['200_day_MA'] = ta.trend.SMAIndicator(data['Close'], 200).sma_indicator()
    data['OBV'] = ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()
    data['Acc/Dist'] = ta.volume.AccDistIndexIndicator(data['High'], data['Low'], data['Close'], data['Volume']).acc_dist_index()
    rsi = momentum.RSIIndicator(data['Close']).rsi()[-1] 
    adx = ta.trend.ADXIndicator(data['High'], data['Low'], data['Close']).adx()

    # Save technical indicators to CSV
    data[['50_day_MA', '200_day_MA', 'OBV', 'Acc/Dist']].to_csv(f'{ticker}_indicators.csv')

    latest = data['Close'].count()

    # Loop through each ticker and send a request to the OpenAI API
    prompt = f"If {ticker} is currently {(data['Close'][latest-1])}, has a 50 day SMA of {(data['50_day_MA'][latest-1])} a 200 day SMA of {(data['200_day_MA'][latest-1])} an RSI of {rsi} and an ADX of {adx} Is this a bullish, bearish or neutral trend?"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=3800,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract the answer from the API response and print it
    answer = response.choices[0].text.strip()
    print(f"{ticker}: {answer}")
    
    # Plot stock price, 50-day MA, and 200-day MA
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(10, 15), dpi=100)
    ax1.plot(data.index, data['Close'], label='Close Price')
    ax1.plot(data.index, data['50_day_MA'], label='50-day Moving Average')
    ax1.plot(data.index, data['200_day_MA'], label='200-day Moving Average')
    ax1.legend()
    ax1.set_title(f'{ticker} Stock Price, 50-day MA, and 200-day MA')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.text(0, -0.3, f"Analysis for {ticker}:\n\n{answer}", wrap=True, transform=plt.gca().transAxes)
        
    # Plot On-Balance Volume
    ax2.plot(data.index, data['OBV'], label='On-Balance Volume')
    ax2.legend()
    ax2.set_title(f'{ticker} On-Balance Volume')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volume')

    # Plot Accumulation/Distribution Line
    ax3.plot(data.index, data['Acc/Dist'], label='Accumulation/Distribution Line')
    ax3.legend()
    ax3.set_title(f'{ticker} Accumulation/Distribution Line')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Accumulation/Distribution')

    # Save the charts as images
    plt.tight_layout()
    fig.savefig(f'{ticker}_charts.png', bbox_inches='tight')

    # Add the charts to the PDF
    pdf.add_page()
    pdf.image(f'{ticker}_charts.png', x=10, y=20, w=190, h=250)
    
# Save the PDF

pdf.output("stock_charts.pdf") #add date to this file name