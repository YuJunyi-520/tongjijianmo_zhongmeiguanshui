import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import pickle

# 创建文件夹
folders = ['data', 'figures']
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# 生成数据
print('开始生成数据...')

# 日期范围
dates = pd.date_range(start='2017-01-01', end='2025-04-30', freq='M')
n = len(dates)

# 贸易数据
trade_data = pd.DataFrame({
    'date': dates,
    'exports': 10000 + np.random.normal(0, 500, n),
    'imports': 30000 + np.random.normal(0, 800, n),
})
trade_data['trade_balance'] = trade_data['exports'] - trade_data['imports']

# 情感数据
sentiment_data = pd.DataFrame({
    'date': dates,
    'us_confidence': 100 + np.random.normal(0, 3, n),
    'china_confidence': 110 + np.random.normal(0, 2, n),
    'positive_sentiment': 0.5 + np.random.normal(0, 0.05, n),
    'negative_sentiment': 0.3 + np.random.normal(0, 0.05, n)
})

# 区域数据
regions = ['东北', '华北', '华东', '华南', '西南', '西北', '中部']
years = list(range(2017, 2026))
regional_data = {
    'regions': regions,
    'years': years,
    'gdp_growth': {region: [5 + np.random.normal(0, 0.5) for _ in years] for region in regions},
    'unemployment': {region: [4 + np.random.normal(0, 0.3) for _ in years] for region in regions},
    'trade_dependency': {region: [30 + np.random.normal(0, 5) for _ in years] for region in regions}
}

# 战略资源数据
strategic_data = pd.DataFrame({
    'date': dates,
    'rare_earth_supply': 15000 + np.random.normal(0, 500, n),
    'us_dependency': 0.8 - np.linspace(0, 0.3, n) + np.random.normal(0, 0.05, n),
    'conflict_risk': 0.2 + np.random.normal(0, 0.05, n)
})

# 保存数据到CSV
trade_data_csv = trade_data.copy()
sentiment_data_csv = sentiment_data.copy()
strategic_data_csv = strategic_data.copy()

trade_data_csv['date'] = trade_data_csv['date'].dt.strftime('%Y-%m-%d')
sentiment_data_csv['date'] = sentiment_data_csv['date'].dt.strftime('%Y-%m-%d')
strategic_data_csv['date'] = strategic_data_csv['date'].dt.strftime('%Y-%m-%d')

trade_data_csv.to_csv('data/trade_analysis.csv', index=False)
sentiment_data_csv.to_csv('data/sentiment_analysis.csv', index=False)
strategic_data_csv.to_csv('data/strategic_resources_analysis.csv', index=False)

# 保存区域数据
with open('data/regional_data.json', 'w', encoding='utf-8') as f:
    json.dump(regional_data, f, ensure_ascii=False, indent=2)

# 保存完整数据到pickle
all_data = {
    'trade_data': trade_data,
    'sentiment_data': sentiment_data,
    'regional_data': regional_data,
    'strategic_data': strategic_data
}

with open('data/all_data.pkl', 'wb') as f:
    pickle.dump(all_data, f)

print('所有数据生成完成并保存到data目录!') 