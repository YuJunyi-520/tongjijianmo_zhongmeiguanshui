#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
区域经济和失业率数据爬虫
生成中国不同区域的经济数据和失业率数据
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

def generate_regional_economic_data():
    """
    生成区域经济数据
    
    模拟中国不同地区的GDP增速、失业率等数据，
    体现关税战对不同区域的差异化影响
    """
    print("开始生成区域经济数据...")
    
    # 定义中国主要区域
    regions = [
        # 沿海制造业发达地区
        "广东", "江苏", "浙江", "上海", "山东", 
        # 中部地区
        "湖北", "湖南", "河南", "安徽", "江西",
        # 西部地区
        "四川", "重庆", "陕西", "云南", "贵州",
        # 东北地区
        "辽宁", "吉林", "黑龙江",
        # 京津冀
        "北京", "天津", "河北"
    ]
    
    # 区域分类
    region_types = {
        "沿海制造业": ["广东", "江苏", "浙江", "上海", "山东"],
        "中部地区": ["湖北", "湖南", "河南", "安徽", "江西"],
        "西部地区": ["四川", "重庆", "陕西", "云南", "贵州"],
        "东北地区": ["辽宁", "吉林", "黑龙江"],
        "京津冀": ["北京", "天津", "河北"]
    }
    
    # 区域对外贸易依存度（越高受关税影响越大）
    trade_dependency = {
        "广东": 0.9, "江苏": 0.85, "浙江": 0.8, "上海": 0.85, "山东": 0.7,
        "湖北": 0.6, "湖南": 0.5, "河南": 0.4, "安徽": 0.55, "江西": 0.4,
        "四川": 0.3, "重庆": 0.45, "陕西": 0.25, "云南": 0.3, "贵州": 0.1,
        "辽宁": 0.6, "吉林": 0.4, "黑龙江": 0.25,
        "北京": 0.5, "天津": 0.7, "河北": 0.5
    }
    
    # 定义各区域基本参数
    # 2017年的GDP基础水平和基础失业率
    base_gdp = {
        "广东": 8.0, "江苏": 7.8, "浙江": 7.6, "上海": 6.8, "山东": 7.4,
        "湖北": 7.8, "湖南": 8.0, "河南": 8.0, "安徽": 8.5, "江西": 8.9,
        "四川": 8.1, "重庆": 9.3, "陕西": 8.0, "云南": 9.5, "贵州": 10.2,
        "辽宁": 4.2, "吉林": 5.3, "黑龙江": 6.4,
        "北京": 6.7, "天津": 5.5, "河北": 6.8
    }
    
    base_unemployment = {
        "广东": 3.1, "江苏": 3.0, "浙江": 3.2, "上海": 4.0, "山东": 3.3,
        "湖北": 3.8, "湖南": 4.0, "河南": 3.6, "安徽": 3.7, "江西": 3.5,
        "四川": 4.2, "重庆": 3.9, "陕西": 3.8, "云南": 4.0, "贵州": 3.9,
        "辽宁": 5.2, "吉林": 4.9, "黑龙江": 4.5,
        "北京": 1.9, "天津": 3.5, "河北": 3.6
    }
    
    # 年份范围（扩展到2025年）
    years = list(range(2017, 2026))
    
    # 关税战时间线
    tariff_years = {
        2018: 0.3,  # 关税开始，影响30%
        2019: 0.7,  # 关税升级，影响70%
        2020: 0.8,  # 关税持续+疫情，影响80%
        2021: 0.6,  # 关税部分缓和，影响60%
        2022: 0.8,  # 芯片管制加强，影响80%
        2023: 0.8,  # 持续影响
        2024: 0.75, # 新一轮关税调整
        2025: 0.65  # 部分缓和
    }
    
    # 生成数据
    data = []
    
    for region in regions:
        trade_depend = trade_dependency[region]
        region_type = None
        for type_name, type_regions in region_types.items():
            if region in type_regions:
                region_type = type_name
                break
        
        for year in years:
            # 2025年只有第一季度数据
            year_fraction = 1.0
            if year == 2025:
                year_fraction = 0.25  # Q1数据
            
            # 基础增长率随时间自然下降（中国经济增速放缓）
            base_growth = base_gdp[region] * (0.95 ** (year - 2017))
            
            # 关税影响
            tariff_effect = 0
            if year in tariff_years:
                # 关税影响 = 关税影响强度 * 贸易依存度
                tariff_effect = -tariff_years[year] * trade_depend * 2.0
            
            # 区域特殊因素
            if region_type == "东北地区":
                special_factor = -0.5  # 东北本身面临转型挑战
            elif region_type == "西部地区":
                special_factor = 1.0  # 西部开发政策支持
            else:
                special_factor = 0
            
            # 2024年政策支持因素
            policy_support = 0
            if year >= 2024:
                if region_type == "中部地区":
                    policy_support = 0.8  # 中部崛起政策加强
                elif region_type == "西部地区":
                    policy_support = 1.2  # 西部大开发深化
                elif region in ["上海", "北京", "深圳"]:
                    policy_support = 0.5  # 科技创新支持
            
            # 最终GDP增速
            gdp_growth = base_growth + tariff_effect + special_factor + policy_support + 0.5 * np.random.randn()
            gdp_growth = max(0, gdp_growth)  # 确保不为负
            
            # 基础失业率随时间变化（整体改善趋势）
            base_unemp = base_unemployment[region] * (0.98 ** (year - 2017))
            
            # 关税对失业率的影响
            unemp_tariff_effect = 0
            if year in tariff_years:
                # 失业率上升 = 关税影响强度 * 贸易依存度
                unemp_tariff_effect = tariff_years[year] * trade_depend * 0.5
            
            # COVID-19特殊影响
            covid_effect = 0
            if year == 2020:
                covid_effect = 1.0  # 疫情提高失业率
            elif year == 2021:
                covid_effect = 0.5  # 疫情影响减弱
            
            # 2024年新就业政策
            employment_policy = 0
            if year >= 2024:
                employment_policy = -0.3  # 就业优先政策效果
                
            # 最终失业率
            unemployment_rate = base_unemp + unemp_tariff_effect + covid_effect + employment_policy + 0.2 * np.random.randn()
            unemployment_rate = max(1.5, unemployment_rate)  # 确保合理的下限
            
            # 投资增速（受关税和地区经济活力影响）
            investment_growth = gdp_growth + 1.0 + tariff_effect * 0.5 + 1.0 * np.random.randn()
            
            # 2024年后投资刺激
            if year >= 2024:
                investment_boost = 2.5 - 0.5 * (year - 2024)  # 递减效应
                investment_growth += investment_boost
            
            # 消费增速（受失业率和消费者信心影响）
            consumption_growth = gdp_growth - 0.2 * (unemployment_rate - base_unemployment[region]) + 0.8 * np.random.randn()
            
            # 2024年后消费刺激政策
            if year >= 2024:
                consumption_boost = 1.5
                consumption_growth += consumption_boost
            
            # 确保数据合理性
            investment_growth = max(0, investment_growth)
            consumption_growth = max(0, consumption_growth)
            
            # 2025年数据按比例调整（只有Q1）
            if year == 2025:
                gdp_growth = gdp_growth * 1.1  # Q1通常增速较高
                investment_growth = investment_growth * 1.2  # 年初投资通常较高
            
            data.append({
                'region': region,
                'region_type': region_type,
                'year': year,
                'gdp_growth': round(gdp_growth, 1),
                'unemployment_rate': round(unemployment_rate, 1),
                'investment_growth': round(investment_growth, 1),
                'consumption_growth': round(consumption_growth, 1),
                'trade_dependency': trade_depend,
                'year_fraction': year_fraction if year == 2025 else 1.0  # 标记2025年是部分数据
            })
    
    # 转换为DataFrame并保存
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(save_dir, 'regional_economic_data.csv'), index=False, encoding='utf-8')
    
    # 生成区域间贸易网络数据（用于空间计量分析）
    generate_regional_trade_network(regions)
    
    print(f"区域经济数据生成完成，已保存到: {save_dir}")
    return df

def generate_regional_trade_network(regions):
    """生成区域间贸易网络数据"""
    n = len(regions)
    
    # 生成邻接矩阵
    adjacency = np.zeros((n, n))
    
    # 定义地理邻近关系（简化版）
    neighbors = {
        "广东": ["广西", "湖南", "江西", "福建", "香港", "澳门"],
        "江苏": ["安徽", "山东", "浙江", "上海"],
        "浙江": ["上海", "江苏", "安徽", "江西", "福建"],
        "上海": ["江苏", "浙江"],
        "山东": ["河北", "河南", "安徽", "江苏"],
        "湖北": ["河南", "安徽", "江西", "湖南", "重庆", "陕西"],
        "湖南": ["江西", "广东", "广西", "贵州", "重庆", "湖北"],
        "河南": ["山东", "河北", "山西", "陕西", "湖北", "安徽"],
        "安徽": ["江苏", "浙江", "江西", "湖北", "河南", "山东"],
        "江西": ["浙江", "福建", "广东", "湖南", "湖北", "安徽"],
        "四川": ["重庆", "贵州", "云南", "西藏", "青海", "甘肃", "陕西"],
        "重庆": ["四川", "贵州", "湖南", "湖北", "陕西"],
        "陕西": ["山西", "河南", "湖北", "重庆", "四川", "甘肃", "宁夏", "内蒙古"],
        "云南": ["四川", "贵州", "广西"],
        "贵州": ["云南", "四川", "重庆", "湖南", "广西"],
        "辽宁": ["吉林", "内蒙古", "河北"],
        "吉林": ["黑龙江", "辽宁", "内蒙古"],
        "黑龙江": ["吉林", "内蒙古"],
        "北京": ["天津", "河北"],
        "天津": ["北京", "河北"],
        "河北": ["北京", "天津", "山东", "河南", "山西", "内蒙古", "辽宁"]
    }
    
    # 转换成邻接矩阵
    for i, region1 in enumerate(regions):
        for j, region2 in enumerate(regions):
            if i == j:
                continue  # 忽略自环
            
            # 如果region2在region1的邻居列表中
            if region2 in neighbors.get(region1, []) or region1 in neighbors.get(region2, []):
                adjacency[i, j] = 1
    
    # 生成贸易流量数据（基于邻接关系和经济规模）
    trade_flows = []
    
    # 扩展年份范围到2025
    for year in range(2017, 2026):
        # 2025年只有Q1数据
        year_fraction = 1.0
        if year == 2025:
            year_fraction = 0.25
            
        for i, region1 in enumerate(regions):
            for j, region2 in enumerate(regions):
                if i == j:
                    continue  # 忽略自环
                
                # 邻近地区贸易流量更大
                is_neighbor = adjacency[i, j] > 0
                neighbor_factor = 2.0 if is_neighbor else 1.0
                
                # 距离衰减（简化模型）
                distance_decay = np.random.uniform(0.5, 1.5) * neighbor_factor
                
                # 基础贸易流量（假设是双向的，但不完全对称）
                base_flow = 100 * distance_decay * np.random.uniform(0.8, 1.2)
                
                # 关税战后区域间贸易变化
                tariff_effect = 1.0
                if year >= 2018:
                    # 关税战后国内价值链重构，区域间贸易增加
                    tariff_effect = 1.0 + 0.05 * (year - 2017)
                
                # 2024年后新一轮国内大循环政策
                if year >= 2024:
                    tariff_effect += 0.1
                
                flow = base_flow * tariff_effect
                
                # 2025年只有Q1数据
                if year == 2025:
                    flow *= year_fraction
                
                trade_flows.append({
                    'year': year,
                    'origin': region1,
                    'destination': region2,
                    'trade_flow': round(flow, 2),
                    'is_neighbor': int(is_neighbor),
                    'year_fraction': year_fraction
                })
    
    # 转换为DataFrame并保存
    df_trade = pd.DataFrame(trade_flows)
    df_trade.to_csv(os.path.join(save_dir, 'regional_trade_flows.csv'), index=False, encoding='utf-8')
    
    # 创建空间权重矩阵（用于空间计量分析）
    df_spatial = pd.DataFrame(adjacency, columns=regions, index=regions)
    df_spatial.to_csv(os.path.join(save_dir, 'regional_spatial_weights.csv'), encoding='utf-8')
    
    return df_trade

# 为了兼容run_all_crawlers.py中的函数调用方式，添加主函数别名
def get_regional_data():
    """
    兼容run_all_crawlers.py的主函数名称命名模式
    """
    # 调用已有的数据生成函数
    return generate_regional_economic_data()

if __name__ == "__main__":
    generate_regional_economic_data() 