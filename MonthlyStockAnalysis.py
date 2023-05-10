import openai
import pandas as pd
from yahoo_fin import stock_info

# Replace your_api_key with your actual OpenAI API key
openai.api_key = "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"

ticker = 'AAPL'
analyst_info = stock_info.get_analysts_info(ticker)

# Save Growth Estimates to a CSV file
growth_estimates = analyst_info["Growth Estimates"]
growth_estimates.to_csv("growth_estimates.csv")

# Read the CSV file
growth_estimates_df = pd.read_csv("growth_estimates.csv")

# Get the current quarter growth estimate for the stock
current_qtr_growth_estimate = growth_estimates_df.loc[growth_estimates_df['Growth Estimates'] == 'Current Qtr.', ticker].values[0]

# Send the growth estimate to the OpenAI API. Would prefer to send all in one go but it exceeds the token limits so splitting up to stay below them
def ask_openai(question):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=(f"{question} The growth estimate for {ticker} in the current quarter is {current_qtr_growth_estimate}. "
                "Is this a bullish or bearish signal? Please provide a short response."),
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )

    answer = response.choices[0].text.strip()
    return answer

question = "Analyze the stock data and tell me"
response = ask_openai(question)
print(response)
