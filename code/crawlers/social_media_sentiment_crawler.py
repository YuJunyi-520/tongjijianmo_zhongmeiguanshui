#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
社交媒体情感分析爬虫
爬取微博/推特等关于关税和贸易战的讨论，进行情感分析
"""

import requests
import pandas as pd
import numpy as np
import os
import time
import json
import re
from datetime import datetime, timedelta
import random
from collections import Counter

# 创建数据保存目录
save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def generate_social_media_sentiment():
    """
    生成模拟的社交媒体情感数据
    
    在实际应用中，应使用Selenium、requests等工具爬取社交媒体数据，
    并使用情感分析库如SnowNLP、NLTK等进行情感分析
    """
    print("开始生成社交媒体情感数据...")
    
    # 生成周度时间序列（2017年至2025年4月）
    start_date = datetime(2017, 1, 1)
    end_date = datetime(2025, 4, 30)
    
    # 按周采样
    weeks = []
    current = start_date
    while current <= end_date:
        weeks.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=7)
    
    # 关键事件时间点
    events = {
        '2018-03-22': '特朗普签署备忘录，宣布对中国商品加征关税',
        '2018-07-06': '美国对340亿美元中国商品加征25%关税正式实施',
        '2018-08-23': '美国对160亿美元中国商品加征25%关税',
        '2018-09-24': '美国对2000亿美元中国商品加征10%关税',
        '2019-05-10': '美国将2000亿美元中国商品关税从10%上调至25%',
        '2019-09-01': '美国对1200亿美元中国商品加征15%关税',
        '2020-01-15': '中美签署第一阶段经贸协议',
        '2022-10-07': '美国出台芯片出口管制新规',
        '2024-06-15': '美国宣布新一轮对华关税措施',
        '2024-11-05': '美国大选日',
        '2025-01-20': '美国新总统就职'
    }
    
    # 热门话题
    topics = ['关税', '贸易战', '中美关系', '进出口', '关税清单', '经济影响', '股市', '汇率', '失业', 
             '半导体', '稀土', '芯片', '供应链', '脱钩', '科技战', '国家安全', '外交关系']
    
    # 生成模拟数据
    data = []
    
    for week in weeks:
        week_date = datetime.strptime(week, '%Y-%m-%d')
        
        # 确定该周的基本情绪基线
        # 关税战前相对平静，关税实施后负面情绪上升
        if week < '2018-03-22':  # 关税战前
            base_positive = 0.6
            base_negative = 0.3
            base_neutral = 0.1
            base_volume = 100 + 50 * np.random.random()  # 基础讨论量
        elif '2018-03-22' <= week < '2018-07-06':  # 关税宣布至实施
            base_positive = 0.4
            base_negative = 0.5
            base_neutral = 0.1
            base_volume = 500 + 200 * np.random.random()
        elif week >= '2018-07-06' and week < '2024-06-15':  # 关税实施后到2024新关税前
            base_positive = 0.3
            base_negative = 0.6
            base_neutral = 0.1
            base_volume = 800 + 300 * np.random.random()
        elif week >= '2024-06-15' and week < '2024-11-05':  # 2024新关税后到大选前
            base_positive = 0.25
            base_negative = 0.65
            base_neutral = 0.1
            base_volume = 1200 + 400 * np.random.random()
        elif week >= '2024-11-05' and week < '2025-01-20':  # 大选后到新总统就职前
            base_positive = 0.35
            base_negative = 0.55
            base_neutral = 0.1
            base_volume = 1000 + 300 * np.random.random()
        else:  # 2025年新总统就职后
            base_positive = 0.45
            base_negative = 0.45
            base_neutral = 0.1
            base_volume = 800 + 200 * np.random.random()
        
        # 关键事件会引起讨论量激增和情绪波动
        event_effect = 0
        event_name = None
        for event_date, event_desc in events.items():
            days_diff = (week_date - datetime.strptime(event_date, '%Y-%m-%d')).days
            if 0 <= days_diff < 14:  # 事件后两周内有明显影响
                influence = 1.0 - days_diff / 14.0  # 随时间衰减
                event_effect = max(event_effect, influence)
                if days_diff < 7:  # 取最近一周的事件作为本周主要事件
                    event_name = event_desc
        
        # 应用事件效应
        if event_effect > 0:
            # 事件会增加讨论量，并使情绪更加极化（减少中性，增加正面或负面）
            volume_multiplier = 1.0 + 5.0 * event_effect
            
            # 关税相关事件通常导致负面情绪上升
            if event_name and ('关税' in event_name or '芯片' in event_name):
                positive_shift = -0.15 * event_effect
                negative_shift = 0.20 * event_effect
            # 协议签署通常导致正面情绪上升
            elif event_name and ('协议' in event_name or '就职' in event_name):
                positive_shift = 0.15 * event_effect
                negative_shift = -0.10 * event_effect
            # 选举相关事件情绪复杂
            elif event_name and '大选' in event_name:
                positive_shift = 0.05 * event_effect
                negative_shift = 0.05 * event_effect
            else:
                positive_shift = -0.10 * event_effect
                negative_shift = 0.15 * event_effect
            
            neutral_shift = -0.05 * event_effect  # 中性情绪下降
        else:
            volume_multiplier = 1.0
            positive_shift = 0
            negative_shift = 0
            neutral_shift = 0
        
        # 计算最终情绪分布和讨论量
        positive = max(0, min(1, base_positive + positive_shift + 0.05 * np.random.randn()))
        negative = max(0, min(1, base_negative + negative_shift + 0.05 * np.random.randn()))
        # 归一化以确保总和为1
        total = positive + negative
        positive /= total
        negative /= total
        neutral = 0  # 已经归一化为正面+负面=1
        
        volume = base_volume * volume_multiplier * (1 + 0.2 * np.random.randn())
        volume = max(10, int(volume))  # 确保至少有一些讨论
        
        # 生成本周热门话题
        if event_effect > 0.5 and event_name:
            # 如果有重大事件，相关话题会更热门
            hot_topics = [event_name.split('，')[0]]  # 取事件描述的第一部分作为热门话题
            topic_weights = [0.6]  # 赋予高权重
            
            # 添加其他随机话题
            additional_topics = random.sample(topics, 2)
            hot_topics.extend(additional_topics)
            topic_weights.extend([0.2, 0.2])
        else:
            # 随机选择热门话题
            hot_topics = random.sample(topics, 3)
            topic_weights = [0.4, 0.3, 0.3]
        
        data.append({
            'date': week,
            'volume': volume,
            'positive_ratio': round(positive, 3),
            'negative_ratio': round(negative, 3),
            'neutral_ratio': round(neutral, 3),
            'hot_topics': ', '.join(hot_topics),
            'event': event_name if event_effect > 0.3 else None
        })
    
    # 转换为DataFrame并保存
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(save_dir, 'social_media_sentiment_weekly.csv'), index=False, encoding='utf-8')
    
    # 生成每日情感数据样本（仅生成部分重要时期的每日数据）
    generate_daily_sentiment_samples(events)
    
    print(f"社交媒体情感数据生成完成，已保存到: {save_dir}")
    return df

def generate_daily_sentiment_samples(events):
    """生成重要时间点前后的每日情感数据样本"""
    daily_samples = []
    
    for event_date, event_desc in events.items():
        # 生成事件前7天和后14天的每日数据
        event_dt = datetime.strptime(event_date, '%Y-%m-%d')
        start_date = event_dt - timedelta(days=7)
        end_date = event_dt + timedelta(days=14)
        
        current = start_date
        while current <= end_date:
            date_str = current.strftime('%Y-%m-%d')
            
            # 计算与事件的天数差
            days_diff = (current - event_dt).days
            
            # 基于天数差和事件类型设置情绪基线
            if '关税' in event_desc or '芯片' in event_desc:
                # 关税和芯片管制事件
                if days_diff < 0:  # 事件前
                    base_positive = 0.40 + 0.05 * days_diff / 7  # 随接近事件日期降低
                    base_negative = 0.50 - 0.05 * days_diff / 7  # 随接近事件日期升高
                    base_volume = 100 * (1 - days_diff / 14)  # 讨论量随接近事件上升
                elif days_diff == 0:  # 事件当天
                    base_positive = 0.25
                    base_negative = 0.70
                    base_volume = 1000
                else:  # 事件后
                    base_positive = 0.25 + 0.01 * days_diff  # 随时间缓慢恢复
                    base_negative = 0.70 - 0.01 * days_diff  # 随时间缓慢恢复
                    base_volume = 1000 * np.exp(-days_diff / 10)  # 讨论量指数衰减
            elif '协议' in event_desc or '就职' in event_desc:
                # 积极事件
                if days_diff < 0:  # 事件前
                    base_positive = 0.50 + 0.02 * days_diff / 7  # 随接近事件日期上升
                    base_negative = 0.40 - 0.02 * days_diff / 7  # 随接近事件日期降低
                    base_volume = 100 * (1 - days_diff / 14)  # 讨论量随接近事件上升
                elif days_diff == 0:  # 事件当天
                    base_positive = 0.60
                    base_negative = 0.35
                    base_volume = 800
                else:  # 事件后
                    base_positive = 0.60 - 0.01 * days_diff  # 乐观情绪渐渐回归常态
                    base_negative = 0.35 + 0.005 * days_diff  # 负面情绪略微回升
                    base_volume = 800 * np.exp(-days_diff / 7)  # 讨论量指数衰减
            elif '大选' in event_desc:
                # 大选事件
                if days_diff < 0:  # 大选前
                    base_positive = 0.45
                    base_negative = 0.45
                    base_volume = 500 * (1 - days_diff / 14)  # 讨论量大幅上升
                elif days_diff == 0:  # 大选当天
                    base_positive = 0.50
                    base_negative = 0.45
                    base_volume = 2000
                else:  # 大选后
                    base_positive = 0.50 - 0.005 * days_diff  # 情绪波动较小
                    base_negative = 0.45 + 0.005 * days_diff
                    base_volume = 2000 * np.exp(-days_diff / 14)  # 讨论量缓慢衰减
            else:
                # 其他事件
                if days_diff < 0:  # 事件前
                    base_positive = 0.45 + 0.05 * days_diff / 7  # 随接近事件日期降低
                    base_negative = 0.45 - 0.05 * days_diff / 7  # 随接近事件日期升高
                    base_volume = 100 * (1 - days_diff / 14)  # 讨论量随接近事件上升
                elif days_diff == 0:  # 事件当天
                    base_positive = 0.3
                    base_negative = 0.65
                    base_volume = 1000
                else:  # 事件后
                    base_positive = 0.3 + 0.02 * days_diff  # 随时间恢复
                    base_negative = 0.65 - 0.02 * days_diff  # 随时间恢复
                    base_volume = 1000 * np.exp(-days_diff / 7)  # 讨论量指数衰减
            
            # 添加随机波动
            positive = max(0, min(1, base_positive + 0.05 * np.random.randn()))
            negative = max(0, min(1, base_negative + 0.05 * np.random.randn()))
            
            # 归一化
            total = positive + negative
            positive /= total
            negative /= total
            neutral = 0
            
            volume = int(base_volume * (1 + 0.3 * np.random.randn()))
            volume = max(10, volume)
            
            daily_samples.append({
                'date': date_str,
                'event': event_desc if days_diff == 0 else None,
                'days_from_event': days_diff,
                'volume': volume,
                'positive_ratio': round(positive, 3),
                'negative_ratio': round(negative, 3),
                'neutral_ratio': round(neutral, 3)
            })
            
            current += timedelta(days=1)
    
    # 转换为DataFrame并保存
    df = pd.DataFrame(daily_samples)
    df.to_csv(os.path.join(save_dir, 'social_media_sentiment_daily_samples.csv'), index=False, encoding='utf-8')
    
    return df

# 为了兼容run_all_crawlers.py中的函数调用方式，添加主函数别名
def get_sentiment_data():
    """
    兼容run_all_crawlers.py的主函数名称命名模式
    """
    # 调用已有的数据生成函数
    return generate_social_media_sentiment()

if __name__ == "__main__":
    generate_social_media_sentiment()
    print("社交媒体情绪数据生成完成") 