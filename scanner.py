import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# 获取全美股列表
url1 = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
url2 = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"
df1 = pd.read_csv(url1, sep='|')
df2 = pd.read_csv(url2, sep='|')
tickers = pd.concat([df1, df2])['Symbol'].dropna().tolist()
tickers = [t for t in tickers if "$" not in t and "." not in t]

# 策略参数
MA_WINDOW = 10
BIAS_THRESHOLD = 0.005
qualified = []

for ticker in tickers:
    try:
        df = yf.download(ticker, period="20d", interval="1d", progress=False)
        if len(df) < MA_WINDOW + 2:
            continue

        df["MA10"] = df["Close"].rolling(window=MA_WINDOW).mean()
        c1 = df["Close"].iloc[-2] > df["MA10"].iloc[-2]
        c2 = df["Close"].iloc[-1] < df["MA10"].iloc[-1]
        c3 = df["Close"].iloc[-1] > df["MA10"].iloc[-1] * (1 - BIAS_THRESHOLD)
        c4 = df["Close"].iloc[-1] > df["Close"].iloc[-2]

        if c1 and c2 and c3 and c4:
            qualified.append(ticker)
        time.sleep(0.1)  # 避免请求过快
    except:
        continue

now = datetime.now().strftime("%Y-%m-%d")
with open("result.txt", "w") as f:
    f.write(f"✅ Buy Rule 2 符合股票（{now}）\n")
    for q in qualified:
        f.write(f"- {q}\n")

print("✔️ 完成筛选，总共找到：", len(qualified))
