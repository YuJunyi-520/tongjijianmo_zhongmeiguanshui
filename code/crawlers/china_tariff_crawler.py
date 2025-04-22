#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中国关税清单数据爬虫
生成中国对美国征收的反制关税清单数据
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

def generate_china_tariff_data():
    """
    生成中国对美国商品的反制关税清单数据
    
    包括四批主要关税反制措施：
    - 第一批：128个税目商品，约30亿美元 (2018年4月2日宣布，4月2日实施部分，7月6日实施其余)
    - 第二批：545个税目商品，约340亿美元 (2018年6月16日宣布，7月6日实施)
    - 第三批：333个税目商品，约160亿美元 (2018年8月8日宣布，8月23日实施)
    - 第四批：大约5140个税目商品，约600亿美元 (2018年8月3日和9月18日宣布，9月24日实施)
    - 2024年新增关税 (模拟数据)
    """
    print("开始生成中国对美关税清单数据...")
    
    # 定义关税轮次
    tariff_rounds = [
        {
            'round': 1,
            'amount': 30,  # 亿美元
            'date': '2018-04-02',
            'rate': [15, 25],  # 税率百分比
            'product_count': 128,  # 商品数量
            'description': '主要针对美国水果、坚果、猪肉、废铝等产品'
        },
        {
            'round': 2,
            'amount': 340,
            'date': '2018-07-06',
            'rate': 25,
            'product_count': 545,
            'description': '主要针对美国大豆、汽车、水产品等'
        },
        {
            'round': 3,
            'amount': 160,
            'date': '2018-08-23',
            'rate': 25,
            'product_count': 333,
            'description': '主要针对美国煤炭、铜废碎料、医疗设备等'
        },
        {
            'round': 4,
            'amount': 600,
            'date': '2018-09-24',
            'rate': [5, 10],
            'product_count': 5140,
            'description': '广泛覆盖美国各类产品'
        },
        {
            'round': 5,
            'amount': 750,
            'date': '2019-06-01',
            'rate': [5, 10, 20, 25],
            'product_count': 5000,
            'description': '对原有关税商品进行税率上调'
        },
        {
            'round': 6,
            'amount': 400,
            'date': '2024-07-15',
            'rate': [10, 15, 25],
            'product_count': 1250,
            'description': '针对美国农产品、化工品、汽车及高科技产品'
        }
    ]
    
    # 生成HS编码范围（模拟）
    hs_ranges = {
        1: ('07', '08', '02', '76'),  # 蔬菜、水果、肉类、铝
        2: ('12', '87', '03'),  # 油籽、汽车、水产品
        3: ('27', '74', '90'),  # 煤炭、铜、医疗设备
        4: ('01', '02', '03', '04', '05', '06', '07', '08', '10', '12', '15', '16', '19', '20', '22', '24', 
            '27', '28', '29', '30', '33', '34', '38', '39', '40', '42', '44', '48', '49', '52', '54', '55', 
            '59', '60', '61', '62', '63', '64', '65', '68', '69', '70', '71', '72', '73', '74', '76', '82', 
            '83', '84', '85', '86', '87', '89', '90', '91', '94', '95', '96'),  # 广泛品类
        5: ('01', '02', '03', '04', '05', '06', '07', '08', '10', '12', '15', '16', '19', '20', '22', '24',
            '27', '28', '29', '30', '33', '34', '38', '39', '40', '42', '44', '48', '49', '52', '54', '55',
            '59', '60', '61', '62', '63', '64', '65', '68', '69', '70', '71', '72', '73', '74', '76', '82',
            '83', '84', '85', '86', '87', '89', '90', '91', '94', '95', '96'),  # 与第四轮相同，但税率不同
        6: ('02', '03', '04', '08', '10', '12', '22', '27', '28', '29', '30', '38', '39', '84', '85', '87', '90')  # 农产品、化工品、机械设备、电子设备、汽车
    }
    
    # 商品类别
    categories = {
        '01': '活动物',
        '02': '肉及食用杂碎',
        '03': '鱼、甲壳动物、软体动物及其他水生无脊椎动物',
        '04': '乳品、禽蛋、天然蜂蜜等',
        '05': '其他动物产品',
        '06': '活树及其他活植物',
        '07': '食用蔬菜、根及块茎',
        '08': '食用水果及坚果',
        '10': '谷物',
        '12': '油籽、子仁、工业用或药用植物、饲料',
        '15': '动植物油、脂及其分解产品',
        '16': '肉、鱼、甲壳动物等的制品',
        '19': '谷物、面粉、淀粉或乳的制品',
        '20': '蔬菜、水果、坚果或植物其他部分的制品',
        '22': '饮料、酒及醋',
        '24': '烟草及烟草代用品的制品',
        '27': '矿物燃料、矿物油及其产品',
        '28': '无机化学品',
        '29': '有机化学品',
        '30': '药品',
        '33': '精油、香料制品、化妆品或盥洗品',
        '34': '肥皂、有机表面活性剂、洗涤剂等',
        '38': '杂项化学产品',
        '39': '塑料及其制品',
        '40': '橡胶及其制品',
        '42': '皮革制品',
        '44': '木及木制品',
        '48': '纸及纸板',
        '49': '书籍、报纸、印刷图画及其他印刷品',
        '52': '棉花',
        '54': '人造丝',
        '55': '人造短纤维',
        '59': '浸渍、涂布、包覆或层压的纺织物',
        '60': '针织或钩编织物',
        '61': '针织或钩编的服装及衣着附件',
        '62': '非针织或非钩编的服装及衣着附件',
        '63': '其他纺织制成品',
        '64': '鞋靴、护腿和类似品及其零件',
        '65': '帽类及其零件',
        '68': '石料、石膏、水泥、石棉、云母或类似材料的制品',
        '69': '陶瓷产品',
        '70': '玻璃及其制品',
        '71': '天然或养殖珍珠、宝石或半宝石等',
        '72': '钢铁',
        '73': '钢铁制品',
        '74': '铜及其制品',
        '76': '铝及其制品',
        '82': '贱金属工具、器具、利口器、餐具及其零件',
        '83': '贱金属杂项制品',
        '84': '核反应堆、锅炉、机械器具及零件',
        '85': '电机、电气设备及其零件',
        '86': '铁道车辆及其零件',
        '87': '车辆及其零件、附件',
        '89': '船舶及浮动结构体',
        '90': '光学、照相、医疗等设备及零件',
        '91': '钟表及其零件',
        '94': '家具、寝具、灯具等',
        '95': '玩具、游戏或运动用品及其零件',
        '96': '杂项制品'
    }
    
    # 创建对应关系：美国出口中国的主要产品与HS编码
    us_exports_to_china = {
        '大豆': ('12', '油籽类', 140),  # HS编码，产品描述，大致年出口额（亿美元）
        '汽车': ('87', '汽车及零部件', 120),
        '集成电路': ('85', '电子产品', 100),
        '飞机': ('88', '航空器', 150),
        '原油': ('27', '矿物燃料', 40),
        '医疗设备': ('90', '医疗器械', 30),
        '废纸': ('47', '纸浆', 20),
        '猪肉': ('02', '肉类', 15),
        '棉花': ('52', '棉花', 10),
        '铜废碎料': ('74', '铜制品', 25),
        '小麦': ('10', '谷物', 5),
        '乙醇': ('22', '酒精饮料', 8),
        '煤炭': ('27', '矿物燃料', 35),
        '水果坚果': ('08', '水果和坚果', 12),
        '化妆品': ('33', '化妆品', 7),
        '化学品': ('28', '无机化学品', 45),
        '塑料': ('39', '塑料制品', 32),
        '光学设备': ('90', '光学设备', 28),
        '木材': ('44', '木材制品', 18),
        '药品': ('30', '药品', 22)
    }
    
    # 生成详细关税清单数据
    all_tariff_items = []
    
    for round_info in tariff_rounds:
        round_num = round_info['round']
        product_count = round_info['product_count']
        tariff_date = round_info['date']
        
        # 处理多个税率的情况
        if isinstance(round_info['rate'], list):
            tariff_rates = round_info['rate']
        else:
            tariff_rates = [round_info['rate']]
            
        # 该轮次的HS编码范围
        hs_prefixes = hs_ranges[round_num]
        
        for _ in range(product_count):
            # 随机选择一个HS类别
            hs_prefix = random.choice(hs_prefixes)
            category = categories[hs_prefix]
            
            # 创建完整的HS编码 (8位，中国常用)
            hs_suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            hs_code = f"{hs_prefix}{hs_suffix}"
            
            # 随机选择一个关税税率
            tariff_rate = random.choice(tariff_rates)
            
            # 生成模拟的商品描述
            if hs_prefix == '12':
                description = f"美国产{random.choice(['大豆', '花生', '葵花籽', '亚麻籽'])}，{random.choice(['用于食品加工', '用于饲料', '用于压榨油'])}"
            elif hs_prefix == '87':
                description = f"美国产{random.choice(['乘用车', '货车', '越野车'])}，{random.choice(['排量', '功率'])}为{random.randint(1000, 5000)}cc"
            elif hs_prefix == '02':
                description = f"美国产{random.choice(['猪肉', '牛肉', '禽肉'])}，{random.choice(['冷冻', '冷藏', '新鲜'])}，{random.choice(['带骨', '去骨'])}"
            elif hs_prefix == '08':
                description = f"美国产{random.choice(['苹果', '橙子', '樱桃', '核桃', '杏仁'])}，{random.choice(['新鲜', '干燥'])}"
            elif hs_prefix == '84' or hs_prefix == '85':
                description = f"美国产{random.choice(['发动机', '电机', '泵', '阀门', '处理器', '存储器'])}，用于{random.choice(['工业', '农业', '商业', '民用'])}"
            else:
                description = f"美国产{category}产品，规格型号{hs_suffix}"
            
            # MFN基准税率（假设值）
            mfn_rate = round(random.uniform(2.0, 10.0), 1)
            
            # 反制措施后的总税率
            total_rate = mfn_rate + tariff_rate
            
            # 随机生成该产品的年度进口额（单位：百万美元）
            import_value = round(random.uniform(0.1, 200.0), 2)
            
            # 生成记录
            tariff_item = {
                'round': round_num,
                'hs_code': hs_code,
                'product_description': description,
                'category': category,
                'implementation_date': tariff_date,
                'mfn_tariff_rate': mfn_rate,
                'additional_tariff_rate': tariff_rate,
                'total_tariff_rate': total_rate,
                'annual_import_value_millions': import_value
            }
            
            # 对于第5和第6轮，说明具体目的
            if round_num == 5:
                tariff_item['note'] = '针对美国加征关税升级的反制措施'
            elif round_num == 6:
                tariff_item['note'] = '针对美国新一轮加征关税的对等反制措施'
            
            all_tariff_items.append(tariff_item)
    
    # 转换为DataFrame并保存
    df = pd.DataFrame(all_tariff_items)
    output_file = os.path.join(save_dir, 'china_tariffs_on_us.csv')
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"中国对美关税清单数据生成完成，已保存到: {output_file}")
    
    # 生成关税影响汇总数据
    generate_tariff_impact_summary()
    
    return df

def generate_tariff_impact_summary():
    """生成关税影响的汇总数据"""
    # 年份范围（扩展到2025年）
    years = list(range(2017, 2026))
    
    # 关键品类
    categories = [
        '大豆及油籽',
        '汽车及零部件',
        '电子产品及零部件',
        '飞机及航空设备',
        '水果及坚果',
        '猪肉及肉制品',
        '化学品及原料',
        '医疗设备',
        '能源产品',
        '农产品其他'
    ]
    
    # 关税时间轴上的关键时点
    tariff_events = {
        2018: {
            'early': "对美水果、猪肉等产品加征关税",
            'mid': "对美农产品、汽车等加征25%关税",
            'late': "对美600亿美元商品加征5-10%关税"
        },
        2019: {
            'mid': "对美反制措施升级",
            'late': "豁免部分大豆、猪肉等农产品关税"
        },
        2020: {
            'early': "中美第一阶段协议签署",
            'mid': "大幅增加美国农产品进口"
        },
        2022: {
            'late': "中美贸易保持韧性但结构调整"
        },
        2024: {
            'mid': "新一轮对美反制措施"
        }
    }
    
    # 创建每个品类每年的关税覆盖率和影响数据
    impact_data = []
    
    for category in categories:
        # 设定基础关税税率和覆盖率
        base_tariff_rate = 5.0  # 假设MFN基础税率
        base_coverage = 0.0     # 基础覆盖率
        
        for year in years:
            # 2025年只有第一季度数据
            if year == 2025:
                year_fraction = 0.25
            else:
                year_fraction = 1.0
                
            # 根据时间轴调整关税税率和覆盖率
            # 不同品类受影响程度不同
            if category == '大豆及油籽':
                if year == 2018:
                    coverage = 0.95
                    rate = 25
                elif year == 2019:
                    coverage = 0.7  # 部分豁免
                    rate = 25
                elif year >= 2020 and year <= 2022:
                    coverage = 0.3  # 一阶段协议豁免
                    rate = 25
                elif year >= 2023:
                    coverage = 0.6
                    rate = 25
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            elif category == '汽车及零部件':
                if year >= 2018 and year <= 2019:
                    coverage = 0.85
                    rate = 25
                elif year >= 2020 and year <= 2023:
                    coverage = 0.7
                    rate = 25
                elif year >= 2024:
                    coverage = 0.9
                    rate = 35  # 新一轮关税
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            elif category == '电子产品及零部件':
                if year >= 2018 and year <= 2020:
                    coverage = 0.6
                    rate = 10
                elif year >= 2021 and year <= 2023:
                    coverage = 0.7
                    rate = 10
                elif year >= 2024:
                    coverage = 0.85
                    rate = 15
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            elif category == '飞机及航空设备':
                if year >= 2018 and year <= 2020:
                    coverage = 0.3  # 战略性不完全覆盖
                    rate = 15
                elif year >= 2021 and year <= 2023:
                    coverage = 0.4
                    rate = 15
                elif year >= 2024:
                    coverage = 0.6
                    rate = 20
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            elif category == '水果及坚果':
                if year >= 2018:
                    coverage = 0.9
                    rate = 15
                if year >= 2019:
                    coverage = 0.95
                    rate = 30
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            elif category == '猪肉及肉制品':
                if year == 2018:
                    coverage = 0.9
                    rate = 25
                elif year >= 2019 and year <= 2021:
                    coverage = 0.5  # 非洲猪瘟后部分豁免
                    rate = 25
                elif year >= 2022:
                    coverage = 0.7
                    rate = 25
                else:
                    coverage = base_coverage
                    rate = base_tariff_rate
            else:  # 其他品类
                if year >= 2018 and year <= 2019:
                    coverage = 0.6
                    rate = 10
                elif year >= 2020 and year <= 2023:
                    coverage = 0.7
                    rate = 10
                elif year >= 2024:
                    coverage = 0.8
                    rate = 15
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
                    if category in ['大豆及油籽', '猪肉及肉制品', '农产品其他'] and 'early' in events:
                        event = events['early']
                    elif category in ['汽车及零部件', '电子产品及零部件'] and 'mid' in events:
                        event = events['mid']
                    elif category in ['水果及坚果', '能源产品'] and 'late' in events:
                        event = events['late']
                    elif 'mid' in events:
                        event = events['mid']
            
            # 贸易额基础值（亿美元）与变化
            if category == '大豆及油籽':
                base_value = 140
            elif category == '汽车及零部件':
                base_value = 120
            elif category == '电子产品及零部件':
                base_value = 100
            elif category == '飞机及航空设备':
                base_value = 150
            elif category == '水果及坚果':
                base_value = 12
            elif category == '猪肉及肉制品':
                base_value = 15
            elif category == '化学品及原料':
                base_value = 45
            elif category == '医疗设备':
                base_value = 30
            elif category == '能源产品':
                base_value = 75
            else:
                base_value = 50
            
            # 关税影响（贸易额下降百分比）
            # 简化公式：影响 = 覆盖率 * 税率 * 敏感系数
            sensitivity = {
                '大豆及油籽': 0.8,
                '汽车及零部件': 0.6,
                '电子产品及零部件': 0.4,
                '飞机及航空设备': 0.2,  # 战略产品，敏感度低
                '水果及坚果': 0.7,
                '猪肉及肉制品': 0.5,  # 受非洲猪瘟影响，关税不是唯一因素
                '化学品及原料': 0.4,
                '医疗设备': 0.3,
                '能源产品': 0.6,
                '农产品其他': 0.7
            }
            
            trade_impact = final_coverage * final_rate * sensitivity.get(category, 0.5) / 100
            
            # 考虑贸易转移和替代效应
            if year > 2018:
                years_since_start = year - 2018
                diversion_factor = min(0.6, 0.1 * years_since_start)  # 贸易转移效应
                
                # 非洲猪瘟特殊影响
                if category == '猪肉及肉制品' and year >= 2019 and year <= 2021:
                    special_factor = 0.1  # 猪瘟导致必须进口，减轻关税影响
                    trade_impact *= (1 - special_factor)
                
                # 第一阶段协议特殊影响
                if category in ['大豆及油籽', '能源产品'] and year >= 2020 and year <= 2022:
                    agreement_factor = 0.5  # 协议规定大量增加进口
                    trade_impact *= (1 - agreement_factor)
                
                trade_impact *= (1 - diversion_factor)
            
            # COVID影响
            if year == 2020:
                covid_impact = 0.15  # 额外15%降幅
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
    output_file = os.path.join(save_dir, 'china_tariff_impact_by_category.csv')
    df_impact.to_csv(output_file, index=False, encoding='utf-8')
    
    return df_impact

# 为了兼容run_all_crawlers.py中的函数调用方式，添加主函数别名
def generate_china_data():
    """
    兼容run_all_crawlers.py的主函数名称命名模式
    """
    return generate_china_tariff_data()

if __name__ == "__main__":
    generate_china_tariff_data() 