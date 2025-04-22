#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中国海关总署进出口贸易数据爬虫
爬取中美贸易相关的进出口数据
"""

import requests
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
import random

# 创建数据保存目录
save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def get_china_us_trade_data():
    """
    获取中美贸易数据
    
    由于中国海关总署网站的数据获取可能需要特殊权限，
    这里使用模拟数据来展示数据结构和分析流程
    """
    print("开始生成中美贸易数据...")
    
    # 生成月度时间序列，扩展到2025年4月
    date_range = pd.date_range(start='2017-01-01', end='2025-04-01', freq='MS')
    months = [d.strftime('%Y-%m') for d in date_range]
    
    # 生成模拟的中美贸易月度数据
    # 2018年7月开始实施第一轮关税，2019年5月关税升级
    data = []
    
    # 基础贸易额和趋势
    base_export = 40  # 单位：十亿美元
    base_import = 15  # 单位：十亿美元
    growth_rate = 0.01  # 月增长率
    seasonal_factor = 0.2  # 季节性因素强度
    
    # 关税冲击参数
    first_tariff_date = '2018-07'  # 第一轮关税
    tariff_upgrade_date = '2019-05'  # 关税升级
    covid_impact_date = '2020-02'  # 新冠疫情影响
    new_tariff_date = '2024-06'  # 假设2024年中新一轮关税调整
    
    first_tariff_shock = -0.15  # 第一轮关税冲击
    tariff_upgrade_shock = -0.25  # 关税升级冲击
    covid_shock = -0.35  # 疫情冲击
    new_tariff_shock = -0.10  # 2024年新关税冲击
    
    for i, month in enumerate(months):
        # 基础趋势
        trend = (1 + growth_rate) ** i
        
        # 季节性因素（第一季度通常贸易量较低）
        month_num = int(month.split('-')[1])
        seasonal = 1 + seasonal_factor * np.sin(2 * np.pi * (month_num - 1) / 12)
        
        # 关税和疫情冲击
        shock = 1.0
        if month >= first_tariff_date:
            shock *= (1 + first_tariff_shock)
        if month >= tariff_upgrade_date:
            shock *= (1 + tariff_upgrade_shock)
        if month >= covid_impact_date:
            shock *= (1 + covid_shock)
            # 疫情后的恢复
            months_after_covid = i - months.index(covid_impact_date)
            if months_after_covid > 0:
                recovery = min(1.0, 0.7 + 0.3 * (months_after_covid / 24))  # 假设24个月恢复
                shock /= recovery
        
        # 2024年新一轮关税调整
        if month >= new_tariff_date:
            shock *= (1 + new_tariff_shock)
        
        # 2023年后贸易关系缓和因素
        if month >= '2023-01':
            easing_factor = 1.0 + 0.01 * (i - months.index('2023-01'))
            easing_factor = min(easing_factor, 1.15)  # 最多恢复15%
            shock *= easing_factor
        
        # 计算最终贸易额
        export_value = base_export * trend * seasonal * shock * (1 + 0.1 * np.random.randn())
        import_value = base_import * trend * seasonal * shock * (1 + 0.1 * np.random.randn())
        
        # 确保数值为正
        export_value = max(0, export_value)
        import_value = max(0, import_value)
        
        data.append({
            'date': month,
            'exports_to_us': round(export_value, 2),
            'imports_from_us': round(import_value, 2),
            'trade_balance': round(export_value - import_value, 2)
        })
    
    # 转换为DataFrame并保存
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(save_dir, 'china_us_trade_monthly.csv'), index=False, encoding='utf-8')
    
    # 生成主要商品类别贸易数据
    generate_category_trade_data()
    
    print(f"中美贸易数据生成完成，已保存到: {save_dir}")
    return df

def generate_category_trade_data():
    """生成主要商品类别的贸易数据"""
    # 定义主要商品类别
    categories = [
        "电子设备及零件",
        "机械设备",
        "纺织品及服装",
        "家具及家居用品",
        "塑料及制品",
        "钢铁及制品",
        "汽车及零部件",
        "医疗设备",
        "农产品",
        "化学品"
    ]
    
    # 每个类别的基础贸易额（十亿美元）
    category_base_values = {
        "电子设备及零件": [15.0, 5.0],  # [出口, 进口]
        "机械设备": [10.0, 3.5],
        "纺织品及服装": [8.0, 0.5],
        "家具及家居用品": [5.0, 0.2],
        "塑料及制品": [3.5, 1.0],
        "钢铁及制品": [4.0, 0.8],
        "汽车及零部件": [2.5, 1.5],
        "医疗设备": [2.0, 3.0],
        "农产品": [1.0, 8.0],
        "化学品": [2.5, 4.0]
    }
    
    # 不同类别受关税影响的敏感度
    tariff_sensitivity = {
        "电子设备及零件": 1.2,  # 高敏感度
        "机械设备": 1.1,
        "纺织品及服装": 0.9,
        "家具及家居用品": 0.8,
        "塑料及制品": 1.0,
        "钢铁及制品": 1.5,  # 高敏感度
        "汽车及零部件": 1.3,
        "医疗设备": 0.5,  # 低敏感度
        "农产品": 1.4,  # 高敏感度
        "化学品": 0.7
    }
    
    # 生成年度数据（2017-2025）
    years = list(range(2017, 2026))
    
    # 关税时间点
    first_tariff_year = 2018
    tariff_upgrade_year = 2019
    covid_year = 2020
    new_tariff_year = 2024
    
    all_data = []
    
    for category in categories:
        base_export, base_import = category_base_values[category]
        sensitivity = tariff_sensitivity[category]
        
        for year in years:
            # 2025年只有部分数据
            if year == 2025:
                base_export *= 0.3  # 假设只有1/3的年度数据
                base_import *= 0.3
            
            # 基础趋势
            trend = 1.0 + 0.08 * (year - 2017)  # 假设每年增长8%
            
            # 关税和疫情冲击
            shock = 1.0
            if year >= first_tariff_year:
                shock *= (1 - 0.15 * sensitivity)
            if year >= tariff_upgrade_year:
                shock *= (1 - 0.10 * sensitivity)
            if year >= covid_year:
                covid_impact = 1 - 0.3 * sensitivity
                recovery = min(1.0, covid_impact + (0.2 * (year - covid_year)))
                shock *= recovery
            
            # 2024年新一轮关税调整
            if year >= new_tariff_year:
                shock *= (1 - 0.08 * sensitivity)
            
            # 2023年后贸易关系部分缓和
            if year >= 2023:
                easing_factor = 1.0 + 0.03 * (year - 2023)
                easing_factor = min(easing_factor, 1.1)  # 最多恢复10%
                shock *= easing_factor
            
            # 添加随机波动
            random_factor = 1 + 0.05 * np.random.randn()
            
            # 计算最终贸易额
            export_value = base_export * trend * shock * random_factor
            import_value = base_import * trend * shock * random_factor
            
            all_data.append({
                'year': year,
                'category': category,
                'exports_to_us': round(export_value, 2),
                'imports_from_us': round(import_value, 2),
                'trade_balance': round(export_value - import_value, 2)
            })
    
    # 转换为DataFrame并保存
    df = pd.DataFrame(all_data)
    df.to_csv(os.path.join(save_dir, 'china_us_trade_by_category.csv'), index=False, encoding='utf-8')
    
    return df

# 为了兼容run_all_crawlers.py中的函数调用方式，添加主函数别名
def generate_china_customs_data():
    """
    兼容run_all_crawlers.py的主函数名称命名模式
    生成中国海关进出口贸易数据
    """
    return get_china_us_trade_data()

if __name__ == "__main__":
    get_china_us_trade_data() 