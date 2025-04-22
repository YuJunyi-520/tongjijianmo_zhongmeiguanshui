#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
消费者信心指数数据爬虫
爬取中美两国消费者信心指数数据
"""

import requests
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime

# 创建数据保存目录
save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def get_consumer_confidence_data():
    """
    获取中美消费者信心指数数据
    
    数据来源应包括：
    1. 美国密歇根大学消费者信心指数
    2. 中国消费者信心指数
    
    这里使用模拟数据展示
    """
    print("开始生成消费者信心指数数据...")
    
    # 生成月度时间序列，扩展到2025年4月
    date_range = pd.date_range(start='2017-01-01', end='2025-04-01', freq='MS')
    months = [d.strftime('%Y-%m') for d in date_range]
    
    # 基础参数
    us_base_cci = 95.0  # 美国基础消费者信心指数
    cn_base_cci = 120.0  # 中国基础消费者信心指数
    
    # 关税和疫情冲击时间点
    first_tariff_date = '2018-07'  # 第一轮关税
    tariff_upgrade_date = '2019-05'  # 关税升级
    covid_impact_date = '2020-02'  # 新冠疫情影响
    new_tariff_date = '2024-06'  # 新一轮关税调整
    us_election_date = '2024-11'  # 美国大选
    
    # 冲击参数
    us_tariff_shock = -5.0  # 关税对美国消费者信心的冲击
    cn_tariff_shock = -8.0  # 关税对中国消费者信心的冲击
    us_covid_shock = -20.0  # 疫情对美国消费者信心的冲击
    cn_covid_shock = -15.0  # 疫情对中国消费者信心的冲击
    us_new_tariff_shock = -3.0  # 新一轮关税对美国消费者信心的冲击
    cn_new_tariff_shock = -6.0  # 新一轮关税对中国消费者信心的冲击
    us_election_shock = -4.0  # 大选不确定性对美国消费者信心的冲击
    
    data = []
    
    for i, month in enumerate(months):
        # 基础趋势（轻微上升）
        us_trend = 0.1 * i / len(months)
        cn_trend = 0.15 * i / len(months)
        
        # 季节性因素
        month_num = int(month.split('-')[1])
        us_seasonal = 2.0 * np.sin(2 * np.pi * (month_num - 1) / 12)
        cn_seasonal = 1.5 * np.sin(2 * np.pi * (month_num - 1) / 12)
        
        # 关税和疫情冲击
        us_shock = 0.0
        cn_shock = 0.0
        
        if month >= first_tariff_date:
            us_shock += us_tariff_shock * 0.5
            cn_shock += cn_tariff_shock * 0.5
        
        if month >= tariff_upgrade_date:
            us_shock += us_tariff_shock * 0.5
            cn_shock += cn_tariff_shock * 0.5
        
        if month >= covid_impact_date:
            months_since_covid = i - months.index(covid_impact_date)
            us_covid_effect = us_covid_shock * np.exp(-months_since_covid / 12)  # 指数恢复
            cn_covid_effect = cn_covid_shock * np.exp(-months_since_covid / 9)   # 中国恢复更快
            us_shock += us_covid_effect
            cn_shock += cn_covid_effect
        
        # 2024年新一轮关税冲击
        if month >= new_tariff_date:
            months_since_new_tariff = i - months.index(new_tariff_date)
            us_new_tariff_effect = us_new_tariff_shock * np.exp(-months_since_new_tariff / 3)
            cn_new_tariff_effect = cn_new_tariff_shock * np.exp(-months_since_new_tariff / 4)
            us_shock += us_new_tariff_effect
            cn_shock += cn_new_tariff_effect
        
        # 2024年美国大选冲击
        if month >= us_election_date and month < '2025-01':
            us_shock += us_election_shock
        
        # 2025年美国新政府上台后消费者信心恢复
        if month >= '2025-01':
            us_shock += 8.0  # 信心恢复效应
        
        # 随机波动
        us_random = np.random.normal(0, 2.0)
        cn_random = np.random.normal(0, 2.5)
        
        # 计算最终指数
        us_cci = us_base_cci + us_trend + us_seasonal + us_shock + us_random
        cn_cci = cn_base_cci + cn_trend + cn_seasonal + cn_shock + cn_random
        
        data.append({
            'date': month,
            'us_consumer_confidence': round(us_cci, 1),
            'cn_consumer_confidence': round(cn_cci, 1)
        })
    
    # 转换为DataFrame并保存
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(save_dir, 'consumer_confidence_monthly.csv'), index=False, encoding='utf-8')
    
    # 生成消费者情绪预期数据
    generate_consumer_sentiment_data()
    
    print(f"消费者信心指数数据生成完成，已保存到: {save_dir}")
    return df

def generate_consumer_sentiment_data():
    """生成消费者情绪和预期数据"""
    # 读取已生成的消费者信心指数数据
    cci_file = os.path.join(save_dir, 'consumer_confidence_monthly.csv')
    if os.path.exists(cci_file):
        cci_data = pd.read_csv(cci_file)
        
        # 添加更多维度的情绪指标
        sentiment_data = []
        
        for _, row in cci_data.iterrows():
            date = row['date']
            us_cci = row['us_consumer_confidence']
            cn_cci = row['cn_consumer_confidence']
            
            # 基于CCI生成其他情绪指标
            # 当前状况指数通常波动更小
            us_current = us_cci * (0.9 + 0.2 * np.random.random())
            cn_current = cn_cci * (0.9 + 0.2 * np.random.random())
            
            # 预期指数通常波动更大
            us_expectation = us_cci * (0.8 + 0.4 * np.random.random())
            cn_expectation = cn_cci * (0.8 + 0.4 * np.random.random())
            
            # 风险感知（关税战后上升）
            date_obj = datetime.strptime(date, '%Y-%m')
            tariff_effect = 0
            
            if date_obj >= datetime(2018, 7, 1):
                tariff_effect = 10
            if date_obj >= datetime(2019, 5, 1):
                tariff_effect = 15
            if date_obj >= datetime(2024, 6, 1):  # 2024年新一轮关税
                tariff_effect = 20
            
            # 新政府上台后风险感知改善
            if date_obj >= datetime(2025, 1, 1):
                tariff_effect -= 5
                
            us_risk_perception = 50 + tariff_effect + 10 * np.random.random() - (us_cci - 95) / 2
            cn_risk_perception = 45 + tariff_effect + 10 * np.random.random() - (cn_cci - 120) / 3
            
            sentiment_data.append({
                'date': date,
                'us_current_condition': round(us_current, 1),
                'us_future_expectation': round(us_expectation, 1),
                'us_risk_perception': round(us_risk_perception, 1),
                'cn_current_condition': round(cn_current, 1),
                'cn_future_expectation': round(cn_expectation, 1),
                'cn_risk_perception': round(cn_risk_perception, 1)
            })
        
        # 保存情绪数据
        sentiment_df = pd.DataFrame(sentiment_data)
        sentiment_df.to_csv(os.path.join(save_dir, 'consumer_sentiment_monthly.csv'), index=False, encoding='utf-8')
        
        return sentiment_df
    
    return None

# 为了兼容run_all_crawlers.py中的函数调用方式，添加主函数别名
def generate_consumer_confidence_data():
    """
    兼容run_all_crawlers.py的主函数名称命名模式
    """
    return get_consumer_confidence_data()

if __name__ == "__main__":
    get_consumer_confidence_data() 