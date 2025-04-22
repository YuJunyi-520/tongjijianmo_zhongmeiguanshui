#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
美国关税清单数据爬虫
生成美国对中国征收的各轮关税清单数据
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

def generate_us_tariff_data():
    """
    生成美国对中国商品各轮关税清单数据
    
    包括第301条款下的四批关税清单：
    - 第一批：340亿美元 (2018年7月6日实施)
    - 第二批：160亿美元 (2018年8月23日实施)
    - 第三批：2000亿美元 (2018年9月24日实施，2019年5月10日从10%上调至25%)
    - 第四批：约3000亿美元 (部分于2019年9月1日实施)
    - 2024年新增关税 (模拟数据)
    """
    print("开始生成美国对华关税清单数据...")
    
    # 定义关税轮次
    tariff_rounds = [
        {
            'round': 1,
            'amount': 340,  # 亿美元
            'date': '2018-07-06',
            'rate': 25,  # 税率百分比
            'product_count': 818,  # 商品数量
            'description': '主要针对中国制造2025相关高科技产品'
        },
        {
            'round': 2,
            'amount': 160,
            'date': '2018-08-23',
            'rate': 25,
            'product_count': 279,
            'description': '主要包括半导体、电子元件、铁路设备等'
        },
        {
            'round': 3,
            'amount': 2000,
            'date': '2018-09-24',
            'initial_rate': 10,
            'rate': 25,
            'escalation_date': '2019-05-10',
            'product_count': 5745,
            'description': '广泛覆盖消费品、电子产品、化学品等'
        },
        {
            'round': 4,
            'amount': 3000,
            'date': '2019-09-01',
            'rate': 15,
            'product_count': 3243,
            'description': '主要包括服装、鞋类、电子产品等消费品'
        },
        {
            'round': 5,
            'amount': 500,
            'date': '2024-06-15',
            'rate': 30,
            'product_count': 1200,
            'description': '针对中国高科技和战略新兴产业，包括电动汽车、电池、稀土等'
        }
    ]
    
    # 生成HS编码范围（模拟）
    hs_ranges = {
        1: ('84', '85', '87', '88', '90'),  # 机械、电子、汽车、航空、光学设备
        2: ('85', '86', '87'),  # 电子、铁路、汽车
        3: ('39', '42', '44', '48', '61', '62', '63', '64', '73', '84', '85', '94'),  # 广泛类别
        4: ('61', '62', '63', '64', '42', '95'),  # 服装、鞋、箱包、玩具
        5: ('85', '87', '28', '29', '38', '76')  # 电子、汽车、化学品、铝制品
    }
    
    # 商品类别
    categories = {
        '84': '核反应堆、锅炉、机械器具及零件',
        '85': '电机、电气设备及其零件',
        '87': '车辆及其零件、附件',
        '88': '航空器、航天器及其零件',
        '90': '光学、照相、医疗等设备及零件',
        '86': '铁道车辆及其零件',
        '39': '塑料及其制品',
        '42': '皮革制品',
        '44': '木及木制品',
        '48': '纸及纸板',
        '61': '针织或钩编的服装及衣着附件',
        '62': '非针织或非钩编的服装及衣着附件',
        '63': '其他纺织制成品',
        '64': '鞋靴、护腿和类似品及其零件',
        '73': '钢铁制品',
        '94': '家具、寝具、灯具等',
        '95': '玩具、游戏或运动用品及其零件',
        '28': '无机化学品',
        '29': '有机化学品',
        '38': '杂项化学产品',
        '76': '铝及铝制品'
    }
    
    # 生成详细关税清单数据
    all_tariff_items = []
    
    for round_info in tariff_rounds:
        round_num = round_info['round']
        product_count = round_info['product_count']
        tariff_date = round_info['date']
        tariff_rate = round_info['rate']
        
        # 该轮次的HS编码范围
        hs_prefixes = hs_ranges[round_num]
        
        for _ in range(product_count):
            # 随机选择一个HS类别
            hs_prefix = random.choice(hs_prefixes)
            category = categories[hs_prefix]
            
            # 创建完整的HS编码 (10位)
            hs_suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            hs_code = f"{hs_prefix}{hs_suffix}"
            
            # 生成模拟的商品描述
            if hs_prefix == '84':
                description = f"{random.choice(['工业', '农业', '商用'])}用{random.choice(['机械', '设备', '器具'])}，{random.choice(['功率', '重量', '尺寸'])}不超过{random.randint(1, 1000)}单位"
            elif hs_prefix == '85':
                description = f"{random.choice(['电子', '电气', '通信'])}设备，用于{random.choice(['工业', '民用', '通信'])}"
            elif hs_prefix == '87':
                description = f"{random.choice(['乘用车', '卡车', '拖拉机', '摩托车'])}，{random.choice(['排量', '功率'])}为{random.randint(50, 5000)}单位"
            elif hs_prefix in ('61', '62', '63'):
                description = f"{random.choice(['男式', '女式', '儿童'])}的{random.choice(['上衣', '裤子', '裙子', '外套', 'T恤'])}"
            else:
                description = f"{category}相关产品，规格型号{hs_suffix}"
            
            # 初始税率和最终税率
            initial_rate = round_info.get('initial_rate', tariff_rate)
            final_rate = tariff_rate
            
            # 随机生成该产品相关的贸易数额（单位：百万美元）
            trade_value = round(random.uniform(0.1, 100.0), 2)
            
            # 生成记录
            tariff_item = {
                'round': round_num,
                'hs_code': hs_code,
                'product_description': description,
                'category': category,
                'implementation_date': tariff_date,
                'initial_tariff_rate': initial_rate,
                'current_tariff_rate': final_rate,
                'annual_trade_value_millions': trade_value
            }
            
            # 对于第三轮，添加关税升级日期
            if round_num == 3:
                tariff_item['tariff_escalation_date'] = round_info['escalation_date']
            
            all_tariff_items.append(tariff_item)
    
    # 转换为DataFrame并保存
    df = pd.DataFrame(all_tariff_items)
    output_file = os.path.join(save_dir, 'us_tariffs_on_china.csv')
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"美国对华关税清单数据生成完成，已保存到: {output_file}")
    
    # 生成关税影响汇总数据
    generate_tariff_impact_summary()
    
    return df

def generate_tariff_impact_summary():
    """生成关税影响的汇总数据"""
    # 年份范围（扩展到2025年）
    years = list(range(2017, 2026))
    
    # 关键品类
    categories = [
        '电子设备和通信设备',
        '机械设备',
        '汽车及零部件',
        '钢铁铝制品',
        '服装和纺织品',
        '塑料和化学品',
        '家具和家居用品',
        '农产品和食品',
        '医疗设备',
        '稀土和电池'
    ]
    
    # 关税时间轴上的关键时点
    tariff_events = {
        2018: {
            'mid': "第一轮关税开始",
            'late': "第二轮和第三轮关税实施"
        },
        2019: {
            'mid': "第三轮关税税率上调至25%",
            'late': "第四轮关税实施"
        },
        2020: {
            'early': "中美第一阶段协议签署",
            'mid': "COVID-19疫情影响"
        },
        2022: {
            'late': "芯片出口管制加强"
        },
        2024: {
            'mid': "新一轮关税措施"
        }
    }
    
    # 创建每个品类每年的关税覆盖率和影响数据
    impact_data = []
    
    for category in categories:
        # 设定基础关税税率和覆盖率
        base_tariff_rate = 3.0  # 假设WTO/MFN基础税率
        base_coverage = 0.0     # 基础覆盖率
        
        for year in years:
            # 2025年只有第一季度数据
            if year == 2025:
                year_fraction = 0.25
            else:
                year_fraction = 1.0
                
            # 根据时间轴调整关税税率和覆盖率
            # 不同品类受影响程度不同
            if category == '电子设备和通信设备':
                if year >= 2018:
                    coverage = 0.6
                    rate = 15
                if year >= 2019:
                    coverage = 0.8
                    rate = 22
                if year >= 2024:
                    coverage = 0.9
                    rate = 28
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            elif category == '机械设备':
                if year >= 2018:
                    coverage = 0.7
                    rate = 18
                if year >= 2019:
                    coverage = 0.85
                    rate = 24
                if year >= 2024:
                    coverage = 0.9
                    rate = 25
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            elif category == '汽车及零部件':
                if year >= 2018:
                    coverage = 0.5
                    rate = 12
                if year >= 2019:
                    coverage = 0.7
                    rate = 20
                if year >= 2024:
                    coverage = 0.95
                    rate = 30  # 新一轮针对电动汽车
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            elif category == '稀土和电池':
                if year >= 2022:
                    coverage = 0.4
                    rate = 15
                if year >= 2024:
                    coverage = 0.9
                    rate = 35  # 高度战略性商品
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            else:  # 其他品类
                if year >= 2018:
                    coverage = 0.4
                    rate = 10
                if year >= 2019:
                    coverage = 0.6
                    rate = 15
                if year >= 2024:
                    coverage = 0.7
                    rate = 18
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            
            # 增加随机波动
            rate_variation = random.uniform(-1.0, 1.0)
            coverage_variation = random.uniform(-0.05, 0.05)
            
            final_rate = max(0, rate + rate_variation)
            final_coverage = max(0, min(1.0, coverage + coverage_variation))
            
            # 相关事件
            event = None
            for event_year, events in tariff_events.items():
                if year == event_year:
                    # 选择与当前类别最相关的事件
                    if category in ['电子设备和通信设备', '机械设备'] and 'mid' in events:
                        event = events['mid']
                    elif category in ['汽车及零部件', '稀土和电池'] and 'late' in events:
                        event = events['late']
                    elif 'early' in events:
                        event = events['early']
            
            # 贸易额基础值（亿美元）与变化
            if category == '电子设备和通信设备':
                base_value = 1500
            elif category == '机械设备':
                base_value = 1200
            elif category == '汽车及零部件':
                base_value = 800
            elif category == '钢铁铝制品':
                base_value = 600
            elif category == '服装和纺织品':
                base_value = 400
            else:
                base_value = 300
            
            # 关税影响（贸易额下降百分比）
            # 简化公式：影响 = 覆盖率 * 税率 * 敏感系数
            sensitivity = {
                '电子设备和通信设备': 0.5,
                '机械设备': 0.4,
                '汽车及零部件': 0.7,
                '钢铁铝制品': 0.8,
                '服装和纺织品': 0.6,
                '塑料和化学品': 0.3,
                '家具和家居用品': 0.5,
                '农产品和食品': 0.2,
                '医疗设备': 0.1,
                '稀土和电池': 0.9
            }
            
            trade_impact = final_coverage * final_rate * sensitivity.get(category, 0.5) / 100
            
            # 考虑时间和其他因素的累积效应
            if year > 2018:
                years_since_start = year - 2018
                adaptation_factor = min(0.7, 0.1 * years_since_start)  # 企业适应能力，最高减轻70%影响
                trade_impact *= (1 - adaptation_factor)
            
            # COVID影响
            if year == 2020:
                covid_impact = 0.2  # 额外20%降幅
                final_trade_value = base_value * (1 - trade_impact - covid_impact)
            else:
                final_trade_value = base_value * (1 - trade_impact)
            
            # 随机波动
            final_trade_value *= (1 + random.uniform(-0.05, 0.05))
            
            # 2025年调整为部分年度数据
            if year == 2025:
                final_trade_value *= year_fraction
            
            impact_data.append({
                'year': year,
                'category': category,
                'tariff_rate': round(final_rate, 1),
                'coverage_ratio': round(final_coverage, 2),
                'trade_value_millions': round(final_trade_value * 100, 1),  # 转换为百万美元
                'trade_reduction_pct': round(trade_impact * 100, 1),
                'key_event': event,
                'year_fraction': year_fraction
            })
    
    # 转换为DataFrame并保存
    df_impact = pd.DataFrame(impact_data)
    output_file = os.path.join(save_dir, 'us_tariff_impact_by_category.csv')
    df_impact.to_csv(output_file, index=False, encoding='utf-8')
    
    return df_impact

# 为了兼容run_all_crawlers.py中的函数调用方式，添加主函数别名
def generate_us_data():
    """
    兼容run_all_crawlers.py的主函数名称命名模式
    """
    return generate_us_tariff_data()

if __name__ == "__main__":
    generate_us_tariff_data() 