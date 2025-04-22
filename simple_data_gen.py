import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import pickle
import matplotlib
matplotlib.use('Agg')  # 设置非交互式后端
import matplotlib.pyplot as plt

# 创建必要的输出文件夹
folders = ['figures', 'data']
for folder in folders:
    os.makedirs(folder, exist_ok=True)

print("开始生成模拟数据...")

# 生成贸易数据
print("生成贸易数据...")
start_date = datetime(2017, 1, 1)
end_date = datetime(2025, 4, 30)

dates = pd.date_range(start=start_date, end=end_date, freq='M')
n = len(dates)

# 基础趋势
base_exports = 10000 + np.linspace(0, 2000, n) + np.random.normal(0, 500, n)
base_imports = 30000 + np.linspace(0, 3000, n) + np.random.normal(0, 800, n)

# 关税冲击
tariff_events = [
    datetime(2018, 7, 6),   # 第一轮关税
    datetime(2019, 5, 10),  # 关税提高
    datetime(2020, 1, 15),  # 第一阶段协议
]

exports = base_exports.copy()
imports = base_imports.copy()

for event_date in tariff_events:
    event_idx = min(range(len(dates)), key=lambda i: abs(dates[i] - event_date))
    
    if event_date == datetime(2018, 7, 6):
        exports[event_idx:] -= 1500 * np.exp(-0.05 * np.arange(len(exports) - event_idx))
        imports[event_idx:] -= 2500 * np.exp(-0.04 * np.arange(len(imports) - event_idx))
    elif event_date == datetime(2019, 5, 10):
        exports[event_idx:] -= 1000 * np.exp(-0.06 * np.arange(len(exports) - event_idx))
        imports[event_idx:] -= 1800 * np.exp(-0.05 * np.arange(len(imports) - event_idx))
    elif event_date == datetime(2020, 1, 15):
        exports[event_idx:] += 800 * (1 - np.exp(-0.07 * np.arange(len(exports) - event_idx)))
        imports[event_idx:] += 1200 * (1 - np.exp(-0.06 * np.arange(len(imports) - event_idx)))

# 确保数据有意义
exports = np.maximum(exports, 0)
imports = np.maximum(imports, 0)

trade_balance = exports - imports

# 创建DataFrame
trade_data = pd.DataFrame({
    'date': dates,
    'exports': exports,
    'imports': imports,
    'trade_balance': trade_balance
})

# 保存数据
trade_data.to_csv('data/trade_data.csv', index=False)

# 生成情感数据
print("生成情感和信心指数数据...")
us_confidence = 100 + np.random.normal(0, 3, n)
china_confidence = 110 + np.random.normal(0, 2, n)

for event_date in tariff_events:
    event_idx = min(range(len(dates)), key=lambda i: abs(dates[i] - event_date))
    
    if event_date == datetime(2018, 3, 22):
        us_confidence[event_idx:event_idx+6] -= np.linspace(2, 0, 6)
        china_confidence[event_idx:event_idx+6] -= np.linspace(1.5, 0, 6)
    elif event_date == datetime(2018, 7, 6):
        us_confidence[event_idx:event_idx+8] -= np.linspace(5, 0, 8)
        china_confidence[event_idx:event_idx+8] -= np.linspace(3, 0, 8)
    elif event_date == datetime(2019, 5, 10):
        us_confidence[event_idx:event_idx+7] -= np.linspace(4, 0, 7)
        china_confidence[event_idx:event_idx+7] -= np.linspace(2.5, 0, 7)
    elif event_date == datetime(2020, 1, 15):
        us_confidence[event_idx:event_idx+10] += np.linspace(0, 3, 10)
        china_confidence[event_idx:event_idx+10] += np.linspace(0, 2, 10)

# 社交媒体情感
positive_sentiment = 0.5 + 0.1 * np.sin(np.linspace(0, 4*np.pi, n)) + np.random.normal(0, 0.05, n)
negative_sentiment = 0.3 + 0.1 * np.sin(np.linspace(0, 4*np.pi, n) + np.pi) + np.random.normal(0, 0.05, n)

# 确保数据有意义
positive_sentiment = np.clip(positive_sentiment, 0, 1)
negative_sentiment = np.clip(negative_sentiment, 0, 1)

# 创建DataFrame
sentiment_data = pd.DataFrame({
    'date': dates,
    'us_confidence': us_confidence,
    'china_confidence': china_confidence,
    'positive_sentiment': positive_sentiment,
    'negative_sentiment': negative_sentiment
})

# 保存数据
sentiment_data.to_csv('data/sentiment_data.csv', index=False)

# 生成区域经济数据
print("生成区域经济数据...")
regions = ["东北", "华北", "华东", "华南", "西南", "西北", "中部"]
years = list(range(2017, 2026))

gdp_growth = {}
unemployment = {}
trade_dependency = {}

for region in regions:
    base_growth = np.random.uniform(5, 8)
    base_unemployment = np.random.uniform(3, 5)
    base_dependency = np.random.uniform(20, 50)
    
    # 不同地区受关税影响程度不同
    if region in ["华东", "华南"]:
        impact_factor = 1.5
    elif region in ["东北", "华北"]:
        impact_factor = 1.2
    else:
        impact_factor = 0.8
    
    gdp_growth[region] = []
    unemployment[region] = []
    trade_dependency[region] = []
    
    for year in years:
        if year == 2018:
            growth = base_growth - impact_factor * 0.5 + np.random.normal(0, 0.3)
            unemp = base_unemployment + impact_factor * 0.3 + np.random.normal(0, 0.2)
            depend = base_dependency - impact_factor * 2 + np.random.normal(0, 1)
        elif year == 2019:
            growth = base_growth - impact_factor * 0.8 + np.random.normal(0, 0.3)
            unemp = base_unemployment + impact_factor * 0.5 + np.random.normal(0, 0.2)
            depend = base_dependency - impact_factor * 3 + np.random.normal(0, 1)
        elif year == 2020:
            growth = base_growth - impact_factor * 0.6 + np.random.normal(0, 0.3)
            unemp = base_unemployment + impact_factor * 0.4 + np.random.normal(0, 0.2)
            depend = base_dependency - impact_factor * 2.5 + np.random.normal(0, 1)
        elif year > 2020:
            growth = base_growth - impact_factor * 0.3 + np.random.normal(0, 0.3)
            unemp = base_unemployment + impact_factor * 0.2 + np.random.normal(0, 0.2)
            depend = base_dependency - impact_factor * 1.5 + np.random.normal(0, 1)
        else:
            growth = base_growth + np.random.normal(0, 0.3)
            unemp = base_unemployment + np.random.normal(0, 0.2)
            depend = base_dependency + np.random.normal(0, 1)
        
        gdp_growth[region].append(max(growth, 0))
        unemployment[region].append(max(unemp, 0))
        trade_dependency[region].append(max(depend, 0))

# 创建字典格式的数据
regional_data = {
    "regions": regions,
    "years": years,
    "gdp_growth": gdp_growth,
    "unemployment": unemployment,
    "trade_dependency": trade_dependency
}

# 保存数据
with open('data/regional_data.json', 'w', encoding='utf-8') as f:
    json.dump(regional_data, f, ensure_ascii=False, indent=2)

# 生成战略资源数据
print("生成战略资源数据...")
base_supply = 15000 + np.linspace(0, 3000, n) + np.random.normal(0, 500, n)
base_dependency = 0.85 - np.linspace(0, 0.25, n) + np.random.normal(0, 0.05, n)

supply = base_supply.copy()
dependency = base_dependency.copy()

for event_date in tariff_events:
    event_idx = min(range(len(dates)), key=lambda i: abs(dates[i] - event_date))
    
    if event_date == datetime(2018, 7, 6):
        supply[event_idx:event_idx+6] -= np.linspace(800, 0, 6)
        dependency[event_idx:event_idx+12] -= np.linspace(0.05, 0, 12)
    elif event_date == datetime(2019, 5, 10):
        supply[event_idx:event_idx+8] -= np.linspace(1200, 0, 8)
        dependency[event_idx:event_idx+15] -= np.linspace(0.08, 0, 15)
    elif event_date == datetime(2020, 1, 15):
        supply[event_idx:event_idx+10] += np.linspace(0, 600, 10)
        dependency[event_idx:event_idx+10] += np.linspace(0, 0.03, 10)

# 冲突风险指数
base_risk = 0.2 + 0.1 * np.sin(np.linspace(0, 2*np.pi, n)) + np.random.normal(0, 0.05, n)
risk = base_risk.copy()

for event_date in tariff_events:
    event_idx = min(range(len(dates)), key=lambda i: abs(dates[i] - event_date))
    
    if event_date == datetime(2018, 7, 6):
        risk[event_idx:event_idx+10] += np.linspace(0.15, 0, 10)
    elif event_date == datetime(2019, 5, 10):
        risk[event_idx:event_idx+12] += np.linspace(0.25, 0, 12)
    elif event_date == datetime(2020, 1, 15):
        risk[event_idx:event_idx+8] -= np.linspace(0.1, 0, 8)

# 确保数据有意义
supply = np.maximum(supply, 0)
dependency = np.clip(dependency, 0, 1)
risk = np.clip(risk, 0, 1)

# 创建DataFrame
strategic_data = pd.DataFrame({
    'date': dates,
    'rare_earth_supply': supply,
    'us_dependency': dependency,
    'conflict_risk': risk
})

# 保存数据
strategic_data.to_csv('data/strategic_resources.csv', index=False)

# 保存所有数据
print("保存所有数据...")

# 为CSV导出准备数据
trade_data_csv = trade_data.copy()
sentiment_data_csv = sentiment_data.copy()
strategic_data_csv = strategic_data.copy()

trade_data_csv['date'] = trade_data_csv['date'].dt.strftime('%Y-%m-%d')
sentiment_data_csv['date'] = sentiment_data_csv['date'].dt.strftime('%Y-%m-%d')
strategic_data_csv['date'] = strategic_data_csv['date'].dt.strftime('%Y-%m-%d')

trade_data_csv.to_csv('data/trade_analysis.csv', index=False)
sentiment_data_csv.to_csv('data/sentiment_analysis.csv', index=False)
strategic_data_csv.to_csv('data/strategic_resources_analysis.csv', index=False)

# 保存pickle文件
with open('data/all_data.pkl', 'wb') as f:
    pickle.dump({
        'trade_data': trade_data,
        'sentiment_data': sentiment_data,
        'regional_data': regional_data,
        'strategic_data': strategic_data
    }, f)

print("所有数据已保存到data/all_data.pkl")
print("所有模拟数据生成完成！") 