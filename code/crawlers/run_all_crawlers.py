#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主脚本：运行所有数据爬虫
采集完整数据集用于后续分析
"""

import os
import sys
import time
import traceback
import importlib.util
from datetime import datetime
import pandas as pd

# 添加项目根目录到系统路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

def count_records(result):
    """
    计算结果中的记录数量
    
    Parameters
    ----------
    result : any
        爬虫返回的结果对象
        
    Returns
    -------
    int
        记录数量
    """
    if result is None:
        return 0
    
    if isinstance(result, pd.DataFrame):
        return len(result)
    elif isinstance(result, list):
        return len(result)
    elif isinstance(result, dict):
        # 尝试累加字典中的所有值的长度
        total = 0
        for value in result.values():
            if isinstance(value, (list, pd.DataFrame)):
                total += len(value)
            elif isinstance(value, dict):
                total += count_records(value)
        return total
    
    # 对于其他类型，如果有__len__方法，则调用它
    if hasattr(result, "__len__"):
        return len(result)
    
    # 无法确定记录数
    return 0

def run_all_crawlers():
    """
    运行所有爬虫脚本，收集完整数据集
    
    数据时间范围：2017年1月至2025年4月
    """
    start_time = time.time()
    print("=" * 60)
    print("开始全面数据采集".center(50))
    print("时间范围: 2017年1月 - 2025年4月".center(50))
    print("=" * 60)
    
    # 确保数据目录存在
    raw_data_dir = os.path.join(BASE_DIR, 'data', 'raw')
    processed_data_dir = os.path.join(BASE_DIR, 'data', 'processed')
    os.makedirs(raw_data_dir, exist_ok=True)
    os.makedirs(processed_data_dir, exist_ok=True)
    
    # 爬虫模块列表
    crawler_modules = [
        ('ustr_tariff_crawler', '美国贸易代表关税数据'),
        ('us_tariff_crawler', '美国关税清单数据'),
        ('china_tariff_crawler', '中国关税清单数据'),
        ('china_customs_crawler', '中国海关进出口数据'),
        ('trade_data_crawler', '中美贸易数据'),
        ('social_media_sentiment_crawler', '社交媒体情绪数据'),
        ('consumer_confidence_crawler', '消费者信心指数数据'),
        ('regional_economic_crawler', '区域经济数据'),
        ('strategic_resources_crawler', '战略资源与安全指标数据'),
    ]
    
    # 统计信息
    successful_modules = 0
    total_records = 0
    
    # 依次运行各个爬虫
    for module_name, data_description in crawler_modules:
        crawler_start_time = time.time()
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始采集{data_description}...")
        
        try:
            # 动态导入爬虫模块
            module_path = os.path.join(os.path.dirname(__file__), f"{module_name}.py")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            crawler_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(crawler_module)
            
            # 运行主要爬虫函数（检查不同的函数名）
            result = None
            
            # 检查各种可能的主函数名
            module_main_prefix = module_name.split('_')[0]
            possible_functions = [
                f"generate_{module_main_prefix}_data",  # 例如: generate_us_data
                f"crawl_{module_main_prefix}_data",     # 例如: crawl_us_data
                f"get_{module_main_prefix}_data",       # 例如: get_us_data
                
                # 完整命名模式，例如: generate_ustr_tariff_data
                f"generate_{module_name}_data",
                f"crawl_{module_name}_data",
                f"get_{module_name}_data",
                
                # 包含在文件名中的主要名词
                f"generate_{module_name.split('_')[0]}_{module_name.split('_')[1]}_data",
                
                # 直接使用文件中的具体函数名
                "get_ustr_tariff_lists",
                "generate_us_tariff_data",
                "generate_china_tariff_data",
                "get_china_us_trade_data",
                "crawl_trade_data",
                "generate_social_media_sentiment",
                "get_consumer_confidence_data",
                "generate_regional_economic_data",
                "generate_strategic_resources_data",
                "generate_military_budget_data",
                "generate_conflict_risk_indicators",
                "generate_data",
                "main"
            ]
            
            # 根据爬虫模块名称添加特定的函数名
            if module_name == "china_customs_crawler":
                possible_functions.append("generate_china_customs_data")
            elif module_name == "social_media_sentiment_crawler":
                possible_functions.append("generate_social_media_data")
            elif module_name == "strategic_resources_crawler":
                possible_functions.append("crawl_strategic_resources_data")
            
            # 尝试调用可能的函数
            for func_name in possible_functions:
                if hasattr(crawler_module, func_name):
                    func = getattr(crawler_module, func_name)
                    result = func()
                    break
            
            if result is None:
                print(f"  警告: 未找到{module_name}的主函数")
            
            # 如果是战略资源爬虫，还需调用额外的军事预算和冲突风险指标生成函数
            if module_name == "strategic_resources_crawler":
                if hasattr(crawler_module, "generate_military_budget_data"):
                    crawler_module.generate_military_budget_data()
                if hasattr(crawler_module, "generate_conflict_risk_indicators"):
                    crawler_module.generate_conflict_risk_indicators()
            
            # 打印采集结果汇总
            crawler_end_time = time.time()
            print(f"✓ {data_description}采集完成！耗时: {crawler_end_time - crawler_start_time:.2f}秒")
            
            # 计算并打印记录数
            record_count = count_records(result)
            total_records += record_count
            print(f"  采集记录数: {record_count}")
            
            successful_modules += 1
            
        except Exception as e:
            print(f"✗ {data_description}采集出错:")
            print(f"  错误信息: {str(e)}")
            traceback.print_exc()
    
    end_time = time.time()
    duration = end_time - start_time
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print("\n" + "=" * 60)
    print("全部数据采集完成!".center(50))
    print(f"总耗时: {int(hours)}小时 {int(minutes)}分 {seconds:.2f}秒".center(50))
    print(f"成功模块: {successful_modules}/{len(crawler_modules)}".center(50))
    print(f"总记录数: {total_records}".center(50))
    print("=" * 60)

if __name__ == "__main__":
    run_all_crawlers() 