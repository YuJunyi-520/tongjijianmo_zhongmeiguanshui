#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
贸易数据爬虫
模拟美中双边贸易数据统计
"""

import requests
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta
import random

# 创建数据保存目录
save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def crawl_trade_data():
    """
    模拟爬取美中双边贸易数据
    生成月度和年度贸易统计数据
    """
    print("开始生成美中双边贸易数据...")
    
    # 生成月度贸易数据
    monthly_data = generate_monthly_trade_data()
    monthly_file = os.path.join(save_dir, 'us_china_monthly_trade.csv')
    monthly_data.to_csv(monthly_file, index=False, encoding='utf-8')
    print(f"月度贸易数据生成完成，已保存到: {monthly_file}")
    
    # 生成年度贸易数据（按产品类别）
    annual_category_data = generate_annual_category_trade_data()
    annual_category_file = os.path.join(save_dir, 'us_china_annual_trade_by_category.csv')
    annual_category_data.to_csv(annual_category_file, index=False, encoding='utf-8')
    print(f"年度按类别贸易数据生成完成，已保存到: {annual_category_file}")
    
    # 生成贸易逆差统计
    deficit_data = generate_trade_deficit_data(monthly_data)
    deficit_file = os.path.join(save_dir, 'us_china_trade_deficit.csv')
    deficit_data.to_csv(deficit_file, index=False, encoding='utf-8')
    print(f"贸易逆差数据生成完成，已保存到: {deficit_file}")
    
    return {
        'monthly_data': monthly_data,
        'annual_category_data': annual_category_data,
        'deficit_data': deficit_data
    }

def generate_monthly_trade_data():
    """
    生成月度美中双边贸易数据（2017-2025）
    """
    # 创建日期范围（2017年1月至2025年3月）
    start_date = datetime(2017, 1, 1)
    end_date = datetime(2025, 4, 1)  # 截止到2025年3月
    
    # 月度日期列表
    dates = []
    current_date = start_date
    while current_date < end_date:
        dates.append(current_date)
        # 移到下个月
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
    
    # 基准贸易数据（单位：百万美元）
    # 假设2017年数据为基准
    base_us_exports = 130000 / 12  # 年出口总额约1300亿美元，月均
    base_us_imports = 500000 / 12  # 年进口总额约5000亿美元，月均
    
    # 存储所有月度数据的列表
    monthly_trade_data = []
    
    # 定义关键事件及其影响
    events = {
        # 第一阶段关税（2018年7月）
        datetime(2018, 7, 1): {
            'us_exports_impact': -0.05,  # 美国对华出口下降5%
            'us_imports_impact': -0.03,  # 美国从华进口下降3%
            'description': "美国对华340亿美元商品加征25%关税，中国采取对等反制"
        },
        # 第二阶段关税（2018年8月）
        datetime(2018, 8, 1): {
            'us_exports_impact': -0.03,
            'us_imports_impact': -0.02,
            'description': "美国对华160亿美元商品加征25%关税，中国采取对等反制"
        },
        # 第三阶段关税（2018年9月）
        datetime(2018, 9, 1): {
            'us_exports_impact': -0.07,
            'us_imports_impact': -0.05,
            'description': "美国对华2000亿美元商品加征10%关税，中国对600亿美元商品采取反制"
        },
        # 关税税率上调（2019年5月）
        datetime(2019, 5, 1): {
            'us_exports_impact': -0.08,
            'us_imports_impact': -0.1,
            'description': "美国将2000亿美元中国商品关税从10%上调至25%"
        },
        # 第四阶段关税（2019年9月）
        datetime(2019, 9, 1): {
            'us_exports_impact': -0.05,
            'us_imports_impact': -0.07,
            'description': "美国对华3000亿美元商品分批加征15%关税，中国采取反制"
        },
        # 中美第一阶段协议（2020年1月）
        datetime(2020, 1, 1): {
            'us_exports_impact': 0.15,  # 美国出口增加
            'us_imports_impact': 0.08,
            'description': "中美签署第一阶段经贸协议，中国承诺增加进口"
        },
        # 新冠疫情爆发（2020年3月全球蔓延）
        datetime(2020, 3, 1): {
            'us_exports_impact': -0.25,
            'us_imports_impact': -0.15,
            'description': "新冠疫情全球蔓延，供应链中断"
        },
        # 疫情后恢复（2021年1月）
        datetime(2021, 1, 1): {
            'us_exports_impact': 0.2,
            'us_imports_impact': 0.3,
            'description': "疫情后贸易强劲反弹"
        },
        # 拜登政府维持关税（2021年3月）
        datetime(2021, 3, 1): {
            'us_exports_impact': -0.02,
            'us_imports_impact': -0.02,
            'description': "拜登政府维持对华关税政策"
        },
        # 通胀压力（2022年3月）
        datetime(2022, 3, 1): {
            'us_exports_impact': -0.05,
            'us_imports_impact': -0.05,
            'description': "全球通胀压力上升"
        },
        # 美国芯片出口限制（2022年10月）
        datetime(2022, 10, 1): {
            'us_exports_impact': -0.1,
            'us_imports_impact': -0.03,
            'description': "美国加强高端芯片及设备出口管制"
        },
        # 供应链调整（2023年）
        datetime(2023, 6, 1): {
            'us_exports_impact': -0.03,
            'us_imports_impact': -0.08,
            'description': "全球供应链调整，部分产能转移"
        },
        # 新一轮关税政策（2024年）
        datetime(2024, 7, 1): {
            'us_exports_impact': -0.07,
            'us_imports_impact': -0.09,
            'description': "美国对华启动新一轮关税措施，中国采取对等反制"
        }
    }
    
    # 季节性因素（月度）
    seasonality = {
        1: 0.9,    # 一月（春节前后，贸易通常减少）
        2: 0.7,    # 二月（春节，显著减少）
        3: 1.0,    # 三月
        4: 1.05,   # 四月
        5: 1.1,    # 五月
        6: 1.15,   # 六月（半年结束前，贸易通常增加）
        7: 1.0,    # 七月
        8: 1.05,   # 八月
        9: 1.15,   # 九月
        10: 1.2,   # 十月（为感恩节和圣诞节备货）
        11: 1.15,  # 十一月
        12: 0.95   # 十二月（年底，贸易通常减少）
    }
    
    # 年度增长基准（无贸易摩擦情况下的自然增长）
    annual_growth = {
        2017: 0.0,   # 基准年
        2018: 0.08,  # 8%自然增长
        2019: 0.06,
        2020: 0.04,  # 疫情影响
        2021: 0.1,   # 疫情后恢复
        2022: 0.07,
        2023: 0.05,
        2024: 0.04,
        2025: 0.03
    }
    
    # 累积影响因素（贸易摩擦的长期累积影响）
    cumulative_exports_impact = 0
    cumulative_imports_impact = 0
    
    # 生成每月的贸易数据
    for date in dates:
        # 获取年度基准增长率
        year_growth = annual_growth.get(date.year, 0.0)
        
        # 计算与基准年的年数差异
        years_from_base = date.year - 2017 + date.month/12
        
        # 应用年度增长（复合增长）
        growth_factor = (1 + year_growth) ** years_from_base
        
        # 应用季节性因素
        seasonal_factor = seasonality.get(date.month, 1.0)
        
        # 检查是否有特殊事件发生在当前月份或之前
        # 累积所有过去事件的影响
        for event_date, impact in events.items():
            if date >= event_date and date < event_date + timedelta(days=90):  # 假设事件影响持续3个月
                # 新事件的直接影响
                exports_impact_factor = 1 + impact['us_exports_impact']
                imports_impact_factor = 1 + impact['us_imports_impact']
                event_description = impact['description']
            else:
                exports_impact_factor = 1
                imports_impact_factor = 1
                event_description = None
            
            # 累积长期影响（只对过去的事件）
            if date >= event_date:
                # 长期影响随时间衰减
                months_since_event = (date.year - event_date.year) * 12 + (date.month - event_date.month)
                if months_since_event <= 24:  # 假设影响持续2年
                    decay_factor = 1 - (months_since_event / 24)
                    cumulative_exports_impact += impact['us_exports_impact'] * 0.3 * decay_factor
                    cumulative_imports_impact += impact['us_imports_impact'] * 0.3 * decay_factor
        
        # 计算最终的贸易数据
        us_exports = base_us_exports * growth_factor * seasonal_factor * exports_impact_factor * (1 + cumulative_exports_impact)
        us_imports = base_us_imports * growth_factor * seasonal_factor * imports_impact_factor * (1 + cumulative_imports_impact)
        
        # 添加随机波动（±5%）
        us_exports *= (1 + random.uniform(-0.05, 0.05))
        us_imports *= (1 + random.uniform(-0.05, 0.05))
        
        # 确保数据合理性
        us_exports = max(us_exports, base_us_exports * 0.4)  # 不会低于基准的40%
        us_imports = max(us_imports, base_us_imports * 0.5)  # 不会低于基准的50%
        
        # 组合成记录
        record = {
            'date': date.strftime('%Y-%m'),
            'year': date.year,
            'month': date.month,
            'us_exports_millions': round(us_exports, 1),
            'us_imports_millions': round(us_imports, 1),
            'trade_balance_millions': round(us_exports - us_imports, 1),
            'event': event_description
        }
        
        monthly_trade_data.append(record)
    
    # 转换为DataFrame
    df = pd.DataFrame(monthly_trade_data)
    
    return df

def generate_annual_category_trade_data():
    """
    按产品类别生成年度美中贸易数据
    """
    # 产品类别
    categories = [
        '电子产品',
        '机械设备',
        '家具和寝具',
        '玩具和体育用品',
        '塑料和橡胶制品',
        '车辆及零部件',
        '钢铁制品',
        '服装和纺织品',
        '化学品',
        '农产品',
        '航空器',
        '医疗设备',
        '能源产品',
        '其他商品'
    ]
    
    # 年份
    years = list(range(2017, 2026))
    
    # 类别在美国对华出口中的基础占比（2017年数据）
    export_category_base_ratio = {
        '电子产品': 0.12,
        '机械设备': 0.14,
        '家具和寝具': 0.01,
        '玩具和体育用品': 0.01,
        '塑料和橡胶制品': 0.05,
        '车辆及零部件': 0.08,
        '钢铁制品': 0.02,
        '服装和纺织品': 0.01,
        '化学品': 0.1,
        '农产品': 0.2,
        '航空器': 0.12,
        '医疗设备': 0.05,
        '能源产品': 0.06,
        '其他商品': 0.03
    }
    
    # 类别在美国从华进口中的基础占比（2017年数据）
    import_category_base_ratio = {
        '电子产品': 0.32,
        '机械设备': 0.22,
        '家具和寝具': 0.07,
        '玩具和体育用品': 0.06,
        '塑料和橡胶制品': 0.05,
        '车辆及零部件': 0.03,
        '钢铁制品': 0.02,
        '服装和纺织品': 0.12,
        '化学品': 0.04,
        '农产品': 0.01,
        '航空器': 0.0,
        '医疗设备': 0.02,
        '能源产品': 0.01,
        '其他商品': 0.03
    }
    
    # 各产品类别在贸易战中的受影响程度（敏感度）
    # 数值越高，表示受关税和贸易政策影响越大
    category_sensitivity = {
        '电子产品': 0.7,
        '机械设备': 0.6,
        '家具和寝具': 0.5,
        '玩具和体育用品': 0.4,
        '塑料和橡胶制品': 0.5,
        '车辆及零部件': 0.8,
        '钢铁制品': 0.9,
        '服装和纺织品': 0.6,
        '化学品': 0.5,
        '农产品': 0.9,  # 农产品受贸易战影响很大
        '航空器': 0.3,  # 航空器受影响相对较小
        '医疗设备': 0.4,
        '能源产品': 0.7,
        '其他商品': 0.5
    }
    
    # 年度总贸易额基准（单位：百万美元）
    base_annual_exports = 130000  # 1300亿美元
    base_annual_imports = 500000  # 5000亿美元
    
    # 定义年度贸易变化趋势
    annual_trend = {
        2017: {'exports_change': 0.0, 'imports_change': 0.0},  # 基准年
        2018: {'exports_change': -0.05, 'imports_change': 0.06},  # 贸易战初期
        2019: {'exports_change': -0.12, 'imports_change': -0.08},  # 贸易战加剧
        2020: {'exports_change': -0.15, 'imports_change': -0.02},  # 疫情影响+贸易协议
        2021: {'exports_change': 0.2, 'imports_change': 0.15},     # 疫情后反弹
        2022: {'exports_change': 0.05, 'imports_change': 0.08},
        2023: {'exports_change': 0.02, 'imports_change': 0.05},
        2024: {'exports_change': -0.03, 'imports_change': -0.01},  # 新一轮贸易摩擦
        2025: {'exports_change': -0.02, 'imports_change': -0.02}   # 仅部分年度数据
    }
    
    # 存储所有类别年度数据的列表
    annual_category_data = []
    
    for year in years:
        # 2025年只有第一季度数据
        if year == 2025:
            year_fraction = 0.25
        else:
            year_fraction = 1.0
        
        # 获取当年的总体变化趋势
        trend = annual_trend.get(year, {'exports_change': 0.0, 'imports_change': 0.0})
        exports_trend = trend['exports_change']
        imports_trend = trend['imports_change']
        
        # 计算年度总贸易额
        annual_exports = base_annual_exports * (1 + exports_trend)
        annual_imports = base_annual_imports * (1 + imports_trend)
        
        # 2025年调整为部分年度数据
        if year == 2025:
            annual_exports *= year_fraction
            annual_imports *= year_fraction
        
        # 定义特殊的贸易政策事件
        special_events = {
            2018: "美国开始对中国商品加征关税",
            2019: "中美贸易战全面升级",
            2020: "中美签署第一阶段贸易协议，COVID-19全球扩散",
            2021: "拜登政府继续特朗普时期关税政策，供应链重组",
            2022: "美国加强对华芯片出口限制",
            2023: "供应链持续调整，部分生产转移至越南等国家",
            2024: "美国对华发起新一轮关税措施",
            2025: "中美关系进入新阶段"
        }
        
        event = special_events.get(year)
        
        # 为每个类别生成数据
        for category in categories:
            # 获取基础占比
            base_export_ratio = export_category_base_ratio.get(category, 0.01)
            base_import_ratio = import_category_base_ratio.get(category, 0.01)
            
            # 获取类别敏感度
            sensitivity = category_sensitivity.get(category, 0.5)
            
            # 产品类别占比的年度变化
            # 受贸易战影响较大的类别，其占比会相应变化
            export_ratio_change = 0.0
            import_ratio_change = 0.0
            
            # 根据年份和类别特性调整占比变化
            if year >= 2018:
                # 贸易战开始后的变化，高敏感度类别受影响更大
                export_ratio_change = -0.02 * sensitivity * (year - 2017)  # 最多下降
                import_ratio_change = -0.03 * sensitivity * (year - 2017)  # 最多下降
                
                # 特定类别的特殊处理
                if category == '农产品':
                    if year == 2018 or year == 2019:
                        export_ratio_change = -0.3 * sensitivity  # 农产品出口大幅下降
                    elif year >= 2020 and year <= 2022:
                        export_ratio_change = 0.2  # 第一阶段协议后回升
                
                if category == '电子产品' and year >= 2022:
                    import_ratio_change = -0.1 * sensitivity  # 芯片限制后进口下降
                
                if category == '航空器' and year >= 2019:
                    export_ratio_change = -0.15 * sensitivity  # 波音问题+贸易战
                
                if category == '车辆及零部件' and year >= 2018:
                    import_ratio_change = 0.1  # 中国汽车零部件出口增加
                
                if category == '医疗设备' and year == 2020:
                    export_ratio_change = 0.15  # 疫情期间医疗设备需求增加
                    import_ratio_change = 0.2
            
            # 确保比例不会变为负数，且变化有上限
            export_ratio_change = max(export_ratio_change, -base_export_ratio * 0.8)
            export_ratio_change = min(export_ratio_change, 0.2)
            
            import_ratio_change = max(import_ratio_change, -base_import_ratio * 0.8)
            import_ratio_change = min(import_ratio_change, 0.2)
            
            # 计算最终占比
            final_export_ratio = base_export_ratio + export_ratio_change
            final_import_ratio = base_import_ratio + import_ratio_change
            
            # 添加随机波动
            final_export_ratio *= (1 + random.uniform(-0.1, 0.1))
            final_import_ratio *= (1 + random.uniform(-0.1, 0.1))
            
            # 确保占比为正
            final_export_ratio = max(0.001, final_export_ratio)
            final_import_ratio = max(0.001, final_import_ratio)
            
            # 计算最终类别贸易额
            export_value = annual_exports * final_export_ratio
            import_value = annual_imports * final_import_ratio
            
            record = {
                'year': year,
                'category': category,
                'export_value_millions': round(export_value, 1),
                'import_value_millions': round(import_value, 1),
                'trade_balance_millions': round(export_value - import_value, 1),
                'export_share': round(final_export_ratio, 3),
                'import_share': round(final_import_ratio, 3),
                'event': event,
                'year_fraction': year_fraction
            }
            
            annual_category_data.append(record)
    
    # 转换为DataFrame
    df = pd.DataFrame(annual_category_data)
    
    return df

def generate_trade_deficit_data(monthly_data):
    """
    基于月度数据生成贸易逆差统计
    """
    # 转换日期列为日期类型
    monthly_data['date'] = pd.to_datetime(monthly_data['date'])
    
    # 按年度汇总月度数据
    annual_deficit = monthly_data.groupby('year').agg({
        'us_exports_millions': 'sum',
        'us_imports_millions': 'sum',
        'trade_balance_millions': 'sum'
    }).reset_index()
    
    # 计算与前一年的变化率
    annual_deficit['exports_yoy_change'] = annual_deficit['us_exports_millions'].pct_change() * 100
    annual_deficit['imports_yoy_change'] = annual_deficit['us_imports_millions'].pct_change() * 100
    annual_deficit['deficit_yoy_change'] = annual_deficit['trade_balance_millions'].pct_change() * 100
    
    # 计算贸易逆差占比（占美国GDP的百分比）
    # 使用粗略估计的美国GDP（单位：万亿美元）
    us_gdp = {
        2017: 19.5,
        2018: 20.6,
        2019: 21.4,
        2020: 21.0,
        2021: 23.0,
        2022: 25.0,
        2023: 26.9,
        2024: 28.2,
        2025: 29.5  # 预估
    }
    
    # 将GDP转换为百万美元并计算逆差比例
    annual_deficit['us_gdp_billions'] = annual_deficit['year'].map(us_gdp)
    annual_deficit['us_gdp_millions'] = annual_deficit['us_gdp_billions'] * 1000000
    annual_deficit['deficit_pct_of_gdp'] = -annual_deficit['trade_balance_millions'] / annual_deficit['us_gdp_millions'] * 100
    
    # 2025年只有部分数据，需要特殊处理
    if 2025 in annual_deficit['year'].values:
        idx = annual_deficit.index[annual_deficit['year'] == 2025].tolist()[0]
        annual_deficit.loc[idx, 'deficit_pct_of_gdp'] = annual_deficit.loc[idx, 'deficit_pct_of_gdp'] * 4  # 年化处理
    
    # 关键事件
    events = {
        2017: "特朗普政府上任，贸易赤字关注度提高",
        2018: "美中贸易战开始",
        2019: "关税全面扩大，贸易额下降",
        2020: "第一阶段协议签署，中国承诺增加购买",
        2021: "拜登政府延续关税政策，贸易强劲恢复",
        2022: "通货膨胀压力下贸易格局调整",
        2023: "供应链持续转移，贸易结构变化",
        2024: "新一轮贸易摩擦",
        2025: "数据仅代表第一季度（年化处理）"
    }
    
    annual_deficit['key_event'] = annual_deficit['year'].map(events)
    
    # 删除不需要的列
    annual_deficit = annual_deficit.drop(['us_gdp_millions'], axis=1)
    
    # 四舍五入数值
    annual_deficit['us_exports_millions'] = annual_deficit['us_exports_millions'].round(1)
    annual_deficit['us_imports_millions'] = annual_deficit['us_imports_millions'].round(1)
    annual_deficit['trade_balance_millions'] = annual_deficit['trade_balance_millions'].round(1)
    annual_deficit['exports_yoy_change'] = annual_deficit['exports_yoy_change'].round(1)
    annual_deficit['imports_yoy_change'] = annual_deficit['imports_yoy_change'].round(1)
    annual_deficit['deficit_yoy_change'] = annual_deficit['deficit_yoy_change'].round(1)
    annual_deficit['deficit_pct_of_gdp'] = annual_deficit['deficit_pct_of_gdp'].round(2)
    
    return annual_deficit

if __name__ == "__main__":
    crawl_trade_data() 