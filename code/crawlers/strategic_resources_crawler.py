#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
战略资源依赖性和相关安全指标数据爬虫
包括：
- 稀土和关键矿产依赖程度
- 技术产业链供应关系
- 军事预算和国防支出
- 地缘政治冲突风险指标
"""

import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 基础参数设置
START_DATE = datetime(2017, 1, 1)
END_DATE = datetime(2025, 4, 30)  # 扩展到2025年4月
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')

# 关键事件时间点
KEY_EVENTS = {
    '2018-03-22': '美国宣布对中国商品征收关税',
    '2018-04-02': '中国对美国128种商品加征关税',
    '2018-07-06': '美国对340亿美元中国商品加征25%关税',
    '2018-08-23': '美国对160亿美元中国商品加征25%关税',
    '2018-09-24': '美国对2000亿美元中国商品加征10%关税',
    '2019-05-10': '美国将2000亿美元中国商品关税税率从10%上调至25%',
    '2019-08-01': '美国宣布对剩余3000亿美元中国商品加征10%关税',
    '2019-12-13': '中美第一阶段经贸协议达成',
    '2020-01-15': '中美签署第一阶段经贸协议',
    '2020-02-14': '中美第一阶段经贸协议生效',
    '2020-08-15': '中美第一阶段经贸协议评估会议',
    '2021-01-20': '拜登就任美国总统',
    '2021-10-04': '美国贸易代表戴琪发表对华贸易政策演讲',
    '2022-01-01': '区域全面经济伙伴关系协定生效',
    '2022-02-24': '俄乌冲突爆发',
    '2022-08-09': '美国《芯片与科学法案》签署',
    '2022-10-07': '美国发布对华半导体出口管制新规',
    '2023-08-09': '美国发布对华投资限制行政令',
    '2023-10-15': '中国发布稀土出口管制新规',
    '2024-06-15': '美国宣布新一轮对华关税措施',
    '2024-11-05': '美国大选日',
    '2025-01-20': '美国新总统就职',
}

def generate_strategic_resources_data():
    """
    生成战略资源依赖性数据
    包括稀土和关键矿产的供应、需求和价格数据
    
    返回:
    - 包含战略资源数据的字典
    """
    # 确保输出目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 定义要分析的战略资源
    resources = [
        # 稀土元素
        '镧', '铈', '镨', '钕', '钷', '钐', '铕', '钆', '铽', '镝', '钬', '铒', '铥', '镱', '镥',
        # 关键矿产
        '锂', '钴', '镍', '铜', '钨', '锗', '铟', '钽', '铂族金属', '石墨', '钛', '锆'
    ]
    
    # 创建月度时间序列
    date_range = pd.date_range(start=START_DATE, end=END_DATE, freq='M')
    
    # 为每种资源创建数据
    resources_data = {}
    
    for resource in resources:
        # 初始基础值
        base_price = random.uniform(10, 1000)  # 基础价格
        base_china_supply = random.uniform(30, 60)  # 中国供应占比(%)
        base_us_dependency = 100 - random.uniform(10, 30)  # 美国依赖度(%)
        volatility = random.uniform(0.05, 0.15)  # 价格波动率
        
        resource_data = []
        
        # 生成月度数据
        for date in date_range:
            # 检查是否有关键事件
            date_str = date.strftime('%Y-%m-%d')
            event = None
            event_effect = 0
            
            # 查找最近30天内的事件
            for event_date, event_desc in KEY_EVENTS.items():
                event_date = datetime.strptime(event_date, '%Y-%m-%d')
                days_diff = abs((date.to_pydatetime() - event_date).days)
                
                if days_diff <= 30:
                    event = event_desc
                    # 根据事件计算影响
                    if '关税' in event_desc or '出口管制' in event_desc:
                        event_effect = random.uniform(0.05, 0.15)
                    elif '协议' in event_desc and '达成' in event_desc:
                        event_effect = random.uniform(-0.08, -0.02)
                    elif '冲突' in event_desc:
                        event_effect = random.uniform(0.10, 0.20)
                    break
            
            # 根据时间段调整供应链关系
            time_effect = 0
            
            # 2018 关税战开始
            if date >= datetime(2018, 3, 1) and date <= datetime(2019, 12, 31):
                time_effect = random.uniform(0.02, 0.05) * (date - datetime(2018, 3, 1)).days / 365
            
            # 2020 疫情扰动
            elif date >= datetime(2020, 1, 1) and date <= datetime(2020, 12, 31):
                time_effect = random.uniform(0.05, 0.10)
            
            # 2021-2022 供应链重构
            elif date >= datetime(2021, 1, 1) and date <= datetime(2022, 12, 31):
                time_effect = random.uniform(0.03, 0.08)
            
            # 2023-2025 战略竞争加剧
            elif date >= datetime(2023, 1, 1):
                months_since_2023 = (date.year - 2023) * 12 + date.month
                time_effect = random.uniform(0.05, 0.12) * (1 + months_since_2023 / 24)
            
            # 计算价格变化
            price_change = np.random.normal(0, volatility) + event_effect + time_effect
            price = base_price * (1 + price_change)
            
            # 调整供应占比
            china_supply = min(95, base_china_supply * (1 + time_effect * 0.5))
            us_dependency = max(5, min(95, base_us_dependency * (1 - time_effect * 0.3)))
            
            # 添加随机波动
            china_supply += random.uniform(-2, 2)
            us_dependency += random.uniform(-2, 2)
            
            # 组织数据
            resource_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'resource': resource,
                'price': round(price, 2),
                'price_change': round(price_change * 100, 2),  # 转为百分比
                'china_supply_pct': round(china_supply, 1),
                'us_dependency_pct': round(us_dependency, 1),
                'event': event
            })
        
        resources_data[resource] = resource_data
    
    # 保存数据
    output_file = os.path.join(DATA_DIR, 'strategic_resources_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resources_data, f, ensure_ascii=False, indent=2)
    
    print(f"战略资源依赖性数据已生成并保存至: {output_file}")
    print(f"包含 {len(resources)} 种资源的月度数据，时间范围: {START_DATE.strftime('%Y-%m-%d')} 至 {END_DATE.strftime('%Y-%m-%d')}")
    
    return resources_data

def generate_military_budget_data():
    """
    生成中美两国军事预算和国防支出相关数据
    
    返回:
    - 包含军事预算数据的字典
    """
    # 确保输出目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 创建年度时间序列
    years = list(range(2017, 2026))  # 扩展到2025年
    
    # 初始参数设置
    us_initial_budget = 700  # 美国初始军费(十亿美元)
    china_initial_budget = 230  # 中国初始军费(十亿美元)
    us_growth_rate = 0.03  # 美国年均增长率
    china_growth_rate = 0.07  # 中国年均增长率
    
    # 生成数据
    military_data = {
        'US': [],
        'China': []
    }
    
    for year in years:
        # 计算美国军费
        if year == 2017:
            us_budget = us_initial_budget
        else:
            # 调整增长率
            if year > 2020:
                adj_growth = us_growth_rate * (1 + (year - 2020) * 0.01)
            else:
                adj_growth = us_growth_rate
            
            # 2022年俄乌冲突后增加
            if year >= 2022:
                adj_growth += 0.01
                
            # 2024大选年可能影响
            if year == 2024:
                adj_growth += random.uniform(-0.005, 0.01)
            
            # 2025新政府可能调整
            if year == 2025:
                adj_growth += random.uniform(-0.01, 0.02)
                
            prev_budget = military_data['US'][-1]['budget']
            us_budget = prev_budget * (1 + adj_growth + random.uniform(-0.005, 0.005))
        
        # 计算中国军费
        if year == 2017:
            china_budget = china_initial_budget
        else:
            # 调整增长率
            if year > 2019:
                adj_growth = china_growth_rate * (1 + (year - 2019) * 0.005)
            else:
                adj_growth = china_growth_rate
            
            # 中美贸易战影响
            if 2018 <= year <= 2020:
                adj_growth -= 0.005
            
            # 2022年以后地缘政治因素
            if year >= 2022:
                adj_growth += 0.01
                
            # 2024-2025潜在调整
            if year >= 2024:
                adj_growth += random.uniform(0, 0.015)
                
            prev_budget = military_data['China'][-1]['budget']
            china_budget = prev_budget * (1 + adj_growth + random.uniform(-0.005, 0.005))
        
        # 添加美国数据
        military_data['US'].append({
            'year': year,
            'budget': round(us_budget, 1),  # 十亿美元
            'gdp_pct': round(us_budget / (22000 + (year - 2017) * 1000) * 100, 2),  # GDP占比
            'per_capita': round(us_budget * 1e9 / (330 + (year - 2017) * 2) / 1e6, 0)  # 人均军费(美元)
        })
        
        # 添加中国数据
        military_data['China'].append({
            'year': year,
            'budget': round(china_budget, 1),  # 十亿美元
            'gdp_pct': round(china_budget / (14000 + (year - 2017) * 800) * 100, 2),  # GDP占比
            'per_capita': round(china_budget * 1e9 / (1400 + (year - 2017) * 5) / 1e6, 0)  # 人均军费(美元)
        })
    
    # 添加军事技术投资数据
    tech_categories = [
        'AI与自主系统', '高超音速武器', '太空技术', '网络战', 
        '量子技术', '生物技术', '新型材料', '核现代化'
    ]
    
    tech_investment = {'US': {}, 'China': {}}
    
    for category in tech_categories:
        # 设置基础投资比例
        us_base = random.uniform(0.05, 0.15)
        china_base = random.uniform(0.04, 0.12)
        
        # 根据类别调整
        if category in ['AI与自主系统', '高超音速武器', '太空技术']:
            china_base *= 1.3  # 中国在这些领域可能投入更多
        
        if category in ['核现代化', '网络战']:
            us_base *= 1.2  # 美国在这些领域可能投入更多
            
        tech_investment['US'][category] = []
        tech_investment['China'][category] = []
        
        for i, year in enumerate(years):
            # 随时间增加的技术投资比例
            year_factor = 1 + (year - 2017) * 0.05
            
            # 美国数据
            us_pct = us_base * year_factor * (1 + random.uniform(-0.1, 0.1))
            us_amount = military_data['US'][i]['budget'] * us_pct
            
            tech_investment['US'][category].append({
                'year': year,
                'amount': round(us_amount, 1),  # 十亿美元
                'budget_pct': round(us_pct * 100, 1)  # 占总军费百分比
            })
            
            # 中国数据
            china_pct = china_base * year_factor * (1 + random.uniform(-0.1, 0.1))
            china_amount = military_data['China'][i]['budget'] * china_pct
            
            tech_investment['China'][category].append({
                'year': year,
                'amount': round(china_amount, 1),  # 十亿美元
                'budget_pct': round(china_pct * 100, 1)  # 占总军费百分比
            })
    
    # 合并数据
    military_budget_data = {
        'overall_budget': military_data,
        'tech_investment': tech_investment
    }
    
    # 保存数据
    output_file = os.path.join(DATA_DIR, 'military_budget_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(military_budget_data, f, ensure_ascii=False, indent=2)
    
    print(f"军事预算数据已生成并保存至: {output_file}")
    print(f"包含中美两国年度军费数据，时间范围: 2017年至2025年")
    
    return military_budget_data

def generate_conflict_risk_indicators():
    """
    生成中美关系冲突风险指标
    
    返回:
    - 包含冲突风险指标的字典
    """
    # 确保输出目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 创建月度时间序列
    date_range = pd.date_range(start=START_DATE, end=END_DATE, freq='M')
    
    # 定义风险指标维度
    risk_dimensions = [
        '贸易紧张度', '技术对抗度', '军事对峙风险', 
        '外交关系状态', '舆论敌意度', '第三方盟友协调度'
    ]
    
    # 生成基础数据
    risk_data = {}
    
    for dimension in risk_dimensions:
        # 设置起始基线值 (0-100)
        if dimension == '贸易紧张度':
            baseline = 30
        elif dimension == '技术对抗度':
            baseline = 25
        elif dimension == '军事对峙风险':
            baseline = 20
        elif dimension == '外交关系状态':
            baseline = 35
        elif dimension == '舆论敌意度':
            baseline = 40
        elif dimension == '第三方盟友协调度':
            baseline = 45
        else:
            baseline = 30
            
        risk_data[dimension] = []
        
        # 上一个月的值，初始为基线
        prev_value = baseline
        
        for date in date_range:
            # 检查是否有关键事件
            date_str = date.strftime('%Y-%m-%d')
            events_effect = 0
            event_desc = []
            
            # 查找最近30天内的事件影响
            for event_date, event_desc_text in KEY_EVENTS.items():
                event_date = datetime.strptime(event_date, '%Y-%m-%d')
                days_diff = abs((date.to_pydatetime() - event_date).days)
                
                if days_diff <= 30:
                    event_desc.append(event_desc_text)
                    
                    # 根据事件和维度计算影响
                    if dimension == '贸易紧张度' and ('关税' in event_desc_text or '贸易' in event_desc_text):
                        events_effect += random.uniform(10, 20)
                    elif dimension == '技术对抗度' and ('芯片' in event_desc_text or '科技' in event_desc_text or '出口管制' in event_desc_text):
                        events_effect += random.uniform(8, 15)
                    elif dimension == '军事对峙风险' and ('冲突' in event_desc_text):
                        events_effect += random.uniform(5, 12)
                    elif dimension == '外交关系状态':
                        if '协议' in event_desc_text and '签署' in event_desc_text:
                            events_effect -= random.uniform(5, 10)
                        elif '制裁' in event_desc_text or '限制' in event_desc_text:
                            events_effect += random.uniform(8, 15)
                    elif dimension == '舆论敌意度':
                        if '关税' in event_desc_text or '制裁' in event_desc_text:
                            events_effect += random.uniform(5, 12)
                        elif '协议' in event_desc_text and '签署' in event_desc_text:
                            events_effect -= random.uniform(3, 8)
                    elif dimension == '第三方盟友协调度' and ('盟友' in event_desc_text or '协调' in event_desc_text):
                        events_effect += random.uniform(5, 10)
            
            # 根据时间段调整基本趋势
            trend_effect = 0
            
            # 2018-2019 贸易战升级
            if date >= datetime(2018, 3, 1) and date <= datetime(2019, 12, 31):
                trend_effect = (date - datetime(2018, 3, 1)).days / 365 * random.uniform(8, 15)
            
            # 2020 COVID-19和第一阶段协议
            elif date >= datetime(2020, 1, 1) and date <= datetime(2020, 12, 31):
                if dimension in ['贸易紧张度', '外交关系状态']:
                    trend_effect = -random.uniform(3, 8)  # 贸易协议缓和
                else:
                    trend_effect = random.uniform(5, 10)  # 疫情加剧其他维度
            
            # 2021 拜登政府初期
            elif date >= datetime(2021, 1, 1) and date <= datetime(2021, 12, 31):
                trend_effect = random.uniform(2, 8)  # 总体延续紧张但风格变化
            
            # 2022-2023 战略竞争加剧
            elif date >= datetime(2022, 1, 1) and date <= datetime(2023, 12, 31):
                months_since_2022 = (date.year - 2022) * 12 + date.month
                trend_effect = random.uniform(5, 12) * (1 + months_since_2022 / 24)
            
            # 2024 大选年
            elif date >= datetime(2024, 1, 1) and date <= datetime(2024, 12, 31):
                # 大选年政治周期影响
                if date.month < 11:  # 大选前
                    trend_effect = random.uniform(10, 20)  # 选举前紧张加剧
                else:  # 大选后
                    trend_effect = random.uniform(5, 15)  # 选举后略微缓和
            
            # 2025 新政府初期
            elif date >= datetime(2025, 1, 1):
                trend_effect = random.uniform(0, 10)  # 政策不确定性
            
            # 添加随机波动
            random_effect = np.random.normal(0, 3)
            
            # 计算新值 (保持在0-100范围内)
            new_value = max(0, min(100, prev_value + events_effect + trend_effect + random_effect))
            
            # 添加回归到均值的效应 (长期均值为50)
            mean_reversion = (50 - new_value) * 0.05
            new_value += mean_reversion
            
            # 保存值作为下个月的前值
            prev_value = new_value
            
            # 组织数据
            risk_data[dimension].append({
                'date': date.strftime('%Y-%m-%d'),
                'value': round(new_value, 1),
                'events': event_desc if event_desc else None
            })
    
    # 计算综合风险指数
    composite_risk = []
    weights = {
        '贸易紧张度': 0.2,
        '技术对抗度': 0.2,
        '军事对峙风险': 0.25,
        '外交关系状态': 0.15,
        '舆论敌意度': 0.1,
        '第三方盟友协调度': 0.1
    }
    
    for i in range(len(date_range)):
        date = date_range[i].strftime('%Y-%m-%d')
        weighted_sum = sum(risk_data[dim][i]['value'] * weights[dim] for dim in risk_dimensions)
        
        # 汇总各维度提到的事件
        all_events = []
        for dim in risk_dimensions:
            if risk_data[dim][i]['events']:
                all_events.extend(risk_data[dim][i]['events'])
        # 去除重复事件
        all_events = list(set(all_events)) if all_events else None
        
        composite_risk.append({
            'date': date,
            'value': round(weighted_sum, 1),
            'events': all_events
        })
    
    # 添加综合指数到风险数据中
    risk_data['综合风险指数'] = composite_risk
    
    # 保存数据
    output_file = os.path.join(DATA_DIR, 'conflict_risk_indicators.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(risk_data, f, ensure_ascii=False, indent=2)
    
    print(f"冲突风险指标数据已生成并保存至: {output_file}")
    print(f"包含{len(risk_dimensions)}个风险维度的月度数据，时间范围: {START_DATE.strftime('%Y-%m-%d')} 至 {END_DATE.strftime('%Y-%m-%d')}")
    
    return risk_data

# 为了兼容run_all_crawlers.py中的函数调用方式，添加主函数别名
def crawl_strategic_resources_data():
    """
    兼容run_all_crawlers.py的主函数名称命名模式
    """
    return generate_strategic_resources_data()

if __name__ == "__main__":
    # 运行数据生成函数
    generate_strategic_resources_data()
    generate_military_budget_data()
    generate_conflict_risk_indicators()
    print("所有战略资源与安全指标数据生成完成！") 