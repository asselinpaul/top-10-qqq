import pandas as pd
import argparse

n = 10 # only keep n top holdings

parser = argparse.ArgumentParser()
parser.add_argument('--target', type=int, default=100000)
args = parser.parse_args()
target_usd_value_of_alloc = args.target

url = "https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0?audienceType=Investor&action=download&ticker=QQQ"
df = pd.read_csv(url)

# only keep top n holdings
df = df.nlargest(n, 'Weight')
df['Weight'] = df['Weight'] / df['Weight'].sum()

# Clean up data
if df['Weight'].dtype != 'float64' and df['Weight'].dtype != 'int64':
    df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')

df['Shares/Par Value'] = df['Shares/Par Value'].astype(str)
df['MarketValue'] = df['MarketValue'].astype(str)
df['Shares/Par Value'] = pd.to_numeric(df['Shares/Par Value'].str.replace(',', ''), errors='coerce')
df['MarketValue'] = pd.to_numeric(df['MarketValue'].str.replace(',', ''), errors='coerce')

# Calculate the market value of a single share for each holding
df['MarketValue_per_Share'] = df['MarketValue'] / df['Shares/Par Value']

# Calculate the number of shares to buy for each of the top 10 holdings
df['Shares_to_Hit_Target_Alloc'] = (target_usd_value_of_alloc * df['Weight']) / df['MarketValue_per_Share']
# Round down to the nearest whole number since we can't purchase fractional shares
df['Shares_to_Hit_Target_Alloc'] = df['Shares_to_Hit_Target_Alloc'].apply(lambda x: int(x))

df['Total_Buy'] = df['MarketValue_per_Share'] * df['Shares_to_Hit_Target_Alloc']

print(df[['Holding Ticker', 'Weight', 'MarketValue_per_Share', 'Shares_to_Hit_Target_Alloc', 'Total_Buy']])

total = (df['MarketValue_per_Share'] * df['Shares_to_Hit_Target_Alloc']).sum()
print(f"Total value of top {n} holdings based on share alloc: ${total}")

