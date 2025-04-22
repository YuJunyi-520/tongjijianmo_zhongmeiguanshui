#!/usr/bin/env Rscript
# 中美关税战多维度分析
# R分析脚本

# 加载必要的库
library(tidyverse)
library(ggplot2)
library(lubridate)
library(plm)
library(spdep)
library(jsonlite)
library(knitr)
library(zoo)
library(DT)
library(broom)

# 设置工作目录和数据路径
base_dir <- "../.."  # 相对于脚本位置的根目录
data_dir <- file.path(base_dir, "data", "raw")
output_dir <- file.path(base_dir, "output")

# 创建输出目录（如果不存在）
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# 数据加载函数
load_data <- function() {
  # 加载贸易数据
  us_china_monthly_trade <- read_csv(file.path(data_dir, "us_china_monthly_trade.csv"))
  us_china_annual_trade_by_category <- read_csv(file.path(data_dir, "us_china_annual_trade_by_category.csv"))
  
  # 加载关税数据
  us_tariffs_on_china <- read_csv(file.path(data_dir, "us_tariffs_on_china.csv"))
  china_tariffs_on_us <- read_csv(file.path(data_dir, "china_tariffs_on_us.csv"))
  
  # 加载消费者信心数据
  consumer_confidence <- read_csv(file.path(data_dir, "consumer_confidence_monthly.csv"))
  
  # 加载社交媒体情感数据
  social_media_sentiment <- read_csv(file.path(data_dir, "social_media_sentiment_weekly.csv"))
  
  # 加载区域经济数据
  regional_economic_data <- read_csv(file.path(data_dir, "regional_economic_data.csv"))
  
  # 加载战略资源数据（JSON格式）
  strategic_resources_file <- file.path(data_dir, "strategic_resources_data.json")
  strategic_resources_data <- fromJSON(strategic_resources_file)
  # 转换为数据框
  strategic_resources_df <- bind_rows(lapply(names(strategic_resources_data), function(resource) {
    resource_data <- strategic_resources_data[[resource]]
    resource_data$resource_name <- resource
    return(resource_data)
  }))
  
  # 加载冲突风险指标
  conflict_risk_file <- file.path(data_dir, "conflict_risk_indicators.json")
  conflict_risk_data <- fromJSON(conflict_risk_file)
  
  # 创建一个列表来存储所有数据集
  data_list <- list(
    us_china_monthly_trade = us_china_monthly_trade,
    us_china_annual_trade_by_category = us_china_annual_trade_by_category,
    us_tariffs_on_china = us_tariffs_on_china,
    china_tariffs_on_us = china_tariffs_on_us,
    consumer_confidence = consumer_confidence,
    social_media_sentiment = social_media_sentiment,
    regional_economic_data = regional_economic_data,
    strategic_resources_data = strategic_resources_df,
    conflict_risk_data = conflict_risk_data
  )
  
  return(data_list)
}

# 数据预处理函数
preprocess_data <- function(data_list) {
  # 处理贸易数据 - 转换日期
  data_list$us_china_monthly_trade <- data_list$us_china_monthly_trade %>%
    mutate(date = as.Date(paste0(date, "-01")))
  
  # 处理社交媒体情感数据 - 转换日期
  data_list$social_media_sentiment <- data_list$social_media_sentiment %>%
    mutate(date = as.Date(date))
  
  # 处理消费者信心数据 - 转换日期
  data_list$consumer_confidence <- data_list$consumer_confidence %>%
    mutate(date = as.Date(paste0(date, "-01")))
  
  # 处理战略资源数据 - 转换日期
  data_list$strategic_resources_data <- data_list$strategic_resources_data %>%
    mutate(date = as.Date(date))
  
  # 为区域经济数据创建面板数据标识符
  data_list$regional_economic_data <- data_list$regional_economic_data %>%
    mutate(id = paste(region, year, sep = "_"))
  
  return(data_list)
}

# 关税影响分析
analyze_tariff_impact <- function(data_list) {
  # 分析关税实施前后的贸易变化
  trade_data <- data_list$us_china_monthly_trade
  
  # 标记关税战前后时期
  trade_data <- trade_data %>%
    mutate(
      period = case_when(
        date < as.Date("2018-07-06") ~ "关税战前",
        date >= as.Date("2018-07-06") & date < as.Date("2020-01-15") ~ "关税战激烈期",
        date >= as.Date("2020-01-15") ~ "第一阶段协议后",
        TRUE ~ "其他"
      )
    )
  
  # 计算各时期的贸易统计
  period_stats <- trade_data %>%
    group_by(period) %>%
    summarise(
      avg_exports = mean(us_exports_millions, na.rm = TRUE),
      avg_imports = mean(us_imports_millions, na.rm = TRUE),
      avg_deficit = mean(trade_balance_millions, na.rm = TRUE),
      n = n()
    )
  
  # 创建贸易趋势图
  trade_plot <- ggplot(trade_data, aes(x = date)) +
    geom_line(aes(y = us_exports_millions, color = "美国对华出口")) +
    geom_line(aes(y = us_imports_millions, color = "美国自华进口")) +
    geom_vline(xintercept = as.Date("2018-07-06"), linetype = "dashed", color = "red") +
    geom_vline(xintercept = as.Date("2020-01-15"), linetype = "dashed", color = "blue") +
    annotate("text", x = as.Date("2018-07-06"), y = max(trade_data$us_imports_millions, na.rm = TRUE), 
             label = "首轮关税", hjust = -0.2, color = "red") +
    annotate("text", x = as.Date("2020-01-15"), y = max(trade_data$us_imports_millions, na.rm = TRUE) * 0.9, 
             label = "第一阶段协议", hjust = -0.2, color = "blue") +
    scale_color_manual(values = c("美国对华出口" = "blue", "美国自华进口" = "red")) +
    labs(title = "中美月度贸易额变化 (2017-2025)",
         x = "日期", y = "贸易额 (百万美元)", color = "类型") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  # 保存图表
  ggsave(file.path(output_dir, "trade_trend.png"), trade_plot, width = 10, height = 6)
  
  # 返回分析结果
  return(list(
    period_stats = period_stats,
    trade_plot = trade_plot
  ))
}

# 消费者信心与社交媒体情感分析
analyze_sentiment <- function(data_list) {
  # 整合消费者信心和社交媒体情感数据
  consumer_data <- data_list$consumer_confidence
  sentiment_data <- data_list$social_media_sentiment
  
  # 将社交媒体周度数据汇总为月度数据
  sentiment_monthly <- sentiment_data %>%
    mutate(month = floor_date(date, "month")) %>%
    group_by(month) %>%
    summarise(
      avg_positive = mean(positive_ratio, na.rm = TRUE),
      avg_negative = mean(negative_ratio, na.rm = TRUE),
      total_volume = sum(volume, na.rm = TRUE)
    )
  
  # 将月度日期转换为与消费者信心数据相同的格式
  sentiment_monthly <- sentiment_monthly %>%
    rename(date = month)
  
  # 合并数据集
  combined_sentiment <- consumer_data %>%
    left_join(sentiment_monthly, by = "date")
  
  # 关税事件的时间点
  tariff_events <- c(
    "2018-03-22", # 特朗普签署备忘录
    "2018-07-06", # 第一轮关税
    "2018-08-23", # 第二轮关税
    "2018-09-24", # 第三轮关税
    "2019-05-10", # 关税上调
    "2020-01-15"  # 第一阶段协议
  )
  
  # 分析关税事件前后的消费者信心变化
  event_analysis <- lapply(tariff_events, function(event_date) {
    event_date <- as.Date(event_date)
    before_period <- seq(event_date - days(90), event_date - days(1), by = "day")
    after_period <- seq(event_date, event_date + days(90), by = "day")
    
    before_data <- consumer_data %>%
      filter(date %in% floor_date(before_period, "month")) %>%
      summarise(
        avg_us_confidence = mean(us_consumer_confidence, na.rm = TRUE),
        avg_cn_confidence = mean(cn_consumer_confidence, na.rm = TRUE)
      )
    
    after_data <- consumer_data %>%
      filter(date %in% floor_date(after_period, "month")) %>%
      summarise(
        avg_us_confidence = mean(us_consumer_confidence, na.rm = TRUE),
        avg_cn_confidence = mean(cn_consumer_confidence, na.rm = TRUE)
      )
    
    return(data.frame(
      event_date = event_date,
      us_before = before_data$avg_us_confidence,
      us_after = after_data$avg_us_confidence,
      us_change = after_data$avg_us_confidence - before_data$avg_us_confidence,
      cn_before = before_data$avg_cn_confidence,
      cn_after = after_data$avg_cn_confidence,
      cn_change = after_data$avg_cn_confidence - before_data$avg_cn_confidence
    ))
  })
  
  event_analysis_df <- do.call(rbind, event_analysis)
  
  # 创建消费者信心与社交媒体情感的时间序列图
  sentiment_plot <- ggplot(combined_sentiment, aes(x = date)) +
    geom_line(aes(y = us_consumer_confidence, color = "美国消费者信心")) +
    geom_line(aes(y = cn_consumer_confidence, color = "中国消费者信心")) +
    geom_line(aes(y = avg_negative * 100, color = "社交媒体负面情绪"), linetype = "dashed") +
    geom_vline(xintercept = as.Date(tariff_events), linetype = "dotted", color = "gray40") +
    scale_color_manual(values = c("美国消费者信心" = "blue", "中国消费者信心" = "red", 
                                 "社交媒体负面情绪" = "darkgreen")) +
    labs(title = "消费者信心与社交媒体情感变化 (2017-2025)",
         x = "日期", y = "指数", color = "指标") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  # 保存图表
  ggsave(file.path(output_dir, "sentiment_trend.png"), sentiment_plot, width = 10, height = 6)
  
  # 返回分析结果
  return(list(
    combined_sentiment = combined_sentiment,
    event_analysis = event_analysis_df,
    sentiment_plot = sentiment_plot
  ))
}

# 区域经济差异分析
analyze_regional_impact <- function(data_list) {
  # 获取区域经济数据
  regional_data <- data_list$regional_economic_data
  
  # 计算各地区类型的年均GDP增长率
  region_type_growth <- regional_data %>%
    group_by(region_type, year) %>%
    summarise(
      avg_gdp_growth = mean(gdp_growth, na.rm = TRUE),
      avg_unemployment = mean(unemployment_rate, na.rm = TRUE),
      avg_trade_dependency = mean(trade_dependency, na.rm = TRUE)
    )
  
  # 计算关税战前后的区域影响差异
  pre_tariff <- regional_data %>%
    filter(year < 2018) %>%
    group_by(region_type) %>%
    summarise(
      avg_gdp_growth = mean(gdp_growth, na.rm = TRUE),
      avg_unemployment = mean(unemployment_rate, na.rm = TRUE)
    )
  
  post_tariff <- regional_data %>%
    filter(year >= 2018 & year <= 2020) %>%
    group_by(region_type) %>%
    summarise(
      avg_gdp_growth = mean(gdp_growth, na.rm = TRUE),
      avg_unemployment = mean(unemployment_rate, na.rm = TRUE)
    )
  
  # 合并前后数据进行比较
  regional_comparison <- pre_tariff %>%
    inner_join(post_tariff, by = "region_type", suffix = c("_pre", "_post")) %>%
    mutate(
      gdp_growth_change = avg_gdp_growth_post - avg_gdp_growth_pre,
      unemployment_change = avg_unemployment_post - avg_unemployment_pre
    )
  
  # 创建区域GDP增长率变化图
  regional_plot <- ggplot(region_type_growth, aes(x = year, y = avg_gdp_growth, color = region_type, group = region_type)) +
    geom_line() +
    geom_point() +
    geom_vline(xintercept = 2018, linetype = "dashed", color = "red") +
    annotate("text", x = 2018, y = max(region_type_growth$avg_gdp_growth), 
             label = "关税战开始", hjust = -0.2, color = "red") +
    labs(title = "不同区域类型GDP增长率变化 (2017-2025)",
         x = "年份", y = "平均GDP增长率 (%)", color = "区域类型") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  # 保存图表
  ggsave(file.path(output_dir, "regional_growth.png"), regional_plot, width = 10, height = 6)
  
  # 对贸易依存度与关税战影响进行回归分析
  regional_data_panel <- pdata.frame(regional_data, index = c("region", "year"))
  
  # 关税战对区域经济的面板回归模型
  model <- plm(gdp_growth ~ unemployment_rate + I(year >= 2018) * trade_dependency, 
                data = regional_data_panel, model = "within")
  
  model_summary <- summary(model)
  
  # 返回分析结果
  return(list(
    region_type_growth = region_type_growth,
    regional_comparison = regional_comparison,
    regional_plot = regional_plot,
    model = model,
    model_summary = model_summary
  ))
}

# 战略资源与冲突风险分析
analyze_strategic_resources <- function(data_list) {
  # 获取战略资源数据
  resources_data <- data_list$strategic_resources_data
  
  # 分析中国稀土供应比例与美国依赖度
  rare_earth_data <- resources_data %>%
    filter(grepl("镧|铈|钕|镝|铽|钆", resource_name)) %>%
    group_by(date) %>%
    summarise(
      avg_china_supply = mean(china_supply_pct, na.rm = TRUE),
      avg_us_dependency = mean(us_dependency_pct, na.rm = TRUE),
      avg_price_change = mean(price_change, na.rm = TRUE)
    )
  
  # 标记关税战重要时间点
  rare_earth_data <- rare_earth_data %>%
    mutate(
      tariff_period = case_when(
        date < as.Date("2018-07-06") ~ "关税战前",
        date >= as.Date("2018-07-06") & date < as.Date("2020-01-15") ~ "关税战期间",
        date >= as.Date("2020-01-15") ~ "第一阶段协议后",
        TRUE ~ "其他"
      )
    )
  
  # 计算各时期平均值
  rare_earth_periods <- rare_earth_data %>%
    group_by(tariff_period) %>%
    summarise(
      avg_china_supply = mean(avg_china_supply, na.rm = TRUE),
      avg_us_dependency = mean(avg_us_dependency, na.rm = TRUE),
      avg_price_change = mean(avg_price_change, na.rm = TRUE),
      n = n()
    )
  
  # 创建稀土依赖度变化图
  resources_plot <- ggplot(rare_earth_data, aes(x = date)) +
    geom_line(aes(y = avg_china_supply, color = "中国稀土供应比例")) +
    geom_line(aes(y = avg_us_dependency, color = "美国稀土依赖度")) +
    geom_vline(xintercept = as.Date("2018-07-06"), linetype = "dashed", color = "red") +
    geom_vline(xintercept = as.Date("2020-01-15"), linetype = "dashed", color = "blue") +
    annotate("text", x = as.Date("2018-07-06"), y = max(rare_earth_data$avg_us_dependency, na.rm = TRUE), 
             label = "首轮关税", hjust = -0.2, color = "red") +
    annotate("text", x = as.Date("2020-01-15"), y = max(rare_earth_data$avg_us_dependency, na.rm = TRUE) * 0.95, 
             label = "第一阶段协议", hjust = -0.2, color = "blue") +
    scale_color_manual(values = c("中国稀土供应比例" = "red", "美国稀土依赖度" = "blue")) +
    labs(title = "稀土供应与依赖度变化 (2017-2025)",
         x = "日期", y = "百分比", color = "指标") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  # 保存图表
  ggsave(file.path(output_dir, "strategic_resources.png"), resources_plot, width = 10, height = 6)
  
  # 返回分析结果
  return(list(
    rare_earth_data = rare_earth_data,
    rare_earth_periods = rare_earth_periods,
    resources_plot = resources_plot
  ))
}

# 运行所有分析
run_analysis <- function() {
  # 加载数据
  cat("加载数据...\n")
  data_list <- load_data()
  
  # 预处理数据
  cat("预处理数据...\n")
  data_list <- preprocess_data(data_list)
  
  # 进行各部分分析
  cat("分析关税影响...\n")
  tariff_analysis <- analyze_tariff_impact(data_list)
  
  cat("分析消费者信心与社交媒体情感...\n")
  sentiment_analysis <- analyze_sentiment(data_list)
  
  cat("分析区域经济差异...\n")
  regional_analysis <- analyze_regional_impact(data_list)
  
  cat("分析战略资源与冲突风险...\n")
  strategic_analysis <- analyze_strategic_resources(data_list)
  
  # 返回所有分析结果
  return(list(
    tariff_analysis = tariff_analysis,
    sentiment_analysis = sentiment_analysis,
    regional_analysis = regional_analysis,
    strategic_analysis = strategic_analysis
  ))
}

# 主程序
main <- function() {
  # 运行分析
  results <- run_analysis()
  
  # 保存分析结果为RDS文件，以便在Rmd中使用
  saveRDS(results, file.path(output_dir, "analysis_results.rds"))
  
  cat("分析完成，结果已保存到", file.path(output_dir, "analysis_results.rds"), "\n")
}

# 执行主程序
main() 