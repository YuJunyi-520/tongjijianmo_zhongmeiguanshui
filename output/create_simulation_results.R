#!/usr/bin/env Rscript
# 创建模拟分析结果数据

library(ggplot2)
library(tidyverse)
library(lubridate)

# 创建输出目录
if (!dir.exists("figures")) {
  dir.create("figures", recursive = TRUE)
}

# 1. 创建贸易趋势数据
create_trade_data <- function() {
  # 生成月度时间序列
  dates <- seq(as.Date("2017-01-01"), as.Date("2025-04-01"), by = "month")
  n <- length(dates)
  
  # 模拟美国对华出口
  base_export <- 9000
  exports <- c(
    base_export + runif(18, -1000, 1000),  # 关税前
    base_export * 0.6 + runif(18, -800, 800),  # 关税期间
    base_export * 0.5 + runif(64, -500, 500)   # 协议后
  )
  
  # 模拟美国自华进口
  base_import <- 40000
  imports <- c(
    base_import + runif(18, -5000, 5000),  # 关税前
    base_import * 0.7 + runif(18, -4000, 4000),  # 关税期间
    base_import * 0.6 + runif(64, -3000, 3000)   # 协议后
  )
  
  # 创建贸易数据框
  trade_data <- data.frame(
    date = dates,
    us_exports_millions = exports,
    us_imports_millions = imports,
    trade_balance_millions = exports - imports
  )
  
  # 添加时期标记
  trade_data <- trade_data %>%
    mutate(
      period = case_when(
        date < as.Date("2018-07-06") ~ "关税战前",
        date >= as.Date("2018-07-06") & date < as.Date("2020-01-15") ~ "关税战激烈期",
        date >= as.Date("2020-01-15") ~ "第一阶段协议后",
        TRUE ~ "其他"
      )
    )
  
  # 计算各时期统计
  period_stats <- trade_data %>%
    group_by(period) %>%
    summarise(
      avg_exports = mean(us_exports_millions),
      avg_imports = mean(us_imports_millions),
      avg_deficit = mean(trade_balance_millions),
      n = n()
    )
  
  # 创建贸易趋势图
  trade_plot <- ggplot(trade_data, aes(x = date)) +
    geom_line(aes(y = us_exports_millions, color = "美国对华出口")) +
    geom_line(aes(y = us_imports_millions, color = "美国自华进口")) +
    geom_vline(xintercept = as.Date("2018-07-06"), linetype = "dashed", color = "red") +
    geom_vline(xintercept = as.Date("2020-01-15"), linetype = "dashed", color = "blue") +
    annotate("text", x = as.Date("2018-07-06"), y = max(trade_data$us_imports_millions), 
             label = "首轮关税", hjust = -0.2, color = "red") +
    annotate("text", x = as.Date("2020-01-15"), y = max(trade_data$us_imports_millions) * 0.9, 
             label = "第一阶段协议", hjust = -0.2, color = "blue") +
    scale_color_manual(values = c("美国对华出口" = "blue", "美国自华进口" = "red")) +
    labs(title = "中美月度贸易额变化 (2017-2025)",
         x = "日期", y = "贸易额 (百万美元)", color = "类型") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  # 保存图表
  ggsave("figures/trade_trend.png", trade_plot, width = 10, height = 6)
  
  return(list(
    trade_data = trade_data,
    period_stats = period_stats,
    trade_plot = trade_plot
  ))
}

# 2. 创建消费者信心与社交媒体情感数据
create_sentiment_data <- function() {
  # 生成月度时间序列
  dates <- seq(as.Date("2017-01-01"), as.Date("2025-04-01"), by = "month")
  n <- length(dates)
  
  # 模拟消费者信心指数
  us_confidence <- c(
    rnorm(18, 95, 2),  # 关税前
    rnorm(18, 88, 3),  # 关税期间
    rnorm(64, 90, 2)   # 协议后
  )
  
  cn_confidence <- c(
    rnorm(18, 120, 3),  # 关税前
    rnorm(18, 115, 4),  # 关税期间
    rnorm(64, 110, 3)   # 协议后
  )
  
  # 模拟社交媒体情感数据
  negative_sentiment <- c(
    runif(18, 0.3, 0.4),  # 关税前
    runif(18, 0.6, 0.7),  # 关税期间
    runif(64, 0.4, 0.6)   # 协议后
  )
  
  # 创建数据框
  sentiment_data <- data.frame(
    date = dates,
    us_consumer_confidence = us_confidence,
    cn_consumer_confidence = cn_confidence,
    avg_negative = negative_sentiment
  )
  
  # 关税事件时间点
  tariff_events <- c(
    "2018-03-22", # 特朗普签署备忘录
    "2018-07-06", # 第一轮关税
    "2018-08-23", # 第二轮关税
    "2018-09-24", # 第三轮关税
    "2019-05-10", # 关税上调
    "2020-01-15"  # 第一阶段协议
  )
  
  # 创建情感趋势图
  sentiment_plot <- ggplot(sentiment_data, aes(x = date)) +
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
  ggsave("figures/sentiment_trend.png", sentiment_plot, width = 10, height = 6)
  
  # 分析关税事件前后的消费者信心变化
  event_analysis <- lapply(tariff_events, function(event_date) {
    event_date <- as.Date(event_date)
    event_idx <- which.min(abs(dates - event_date))
    
    before_idx <- max(1, event_idx - 3)
    after_idx <- min(n, event_idx + 3)
    
    before_us <- mean(us_confidence[before_idx:(event_idx-1)])
    after_us <- mean(us_confidence[event_idx:after_idx])
    
    before_cn <- mean(cn_confidence[before_idx:(event_idx-1)])
    after_cn <- mean(cn_confidence[event_idx:after_idx])
    
    return(data.frame(
      event_date = event_date,
      us_before = before_us,
      us_after = after_us,
      us_change = after_us - before_us,
      cn_before = before_cn,
      cn_after = after_cn,
      cn_change = after_cn - before_cn
    ))
  })
  
  event_analysis_df <- do.call(rbind, event_analysis)
  
  return(list(
    sentiment_data = sentiment_data,
    event_analysis = event_analysis_df,
    sentiment_plot = sentiment_plot
  ))
}

# 3. 创建区域经济数据
create_regional_data <- function() {
  # 区域类型
  region_types <- c("沿海制造业", "中部地区", "西部地区", "东北地区", "京津冀")
  
  # 创建区域增长数据
  years <- 2017:2025
  n_years <- length(years)
  n_types <- length(region_types)
  
  # 预设增长率
  growth_rates <- matrix(nrow = n_types, ncol = n_years)
  rownames(growth_rates) <- region_types
  colnames(growth_rates) <- years
  
  # 设置不同区域的基准增长率和关税影响
  growth_rates["沿海制造业",] <- c(7.2, 6.5, 5.5, 4.7, 6.8, 5.5, 3.8, 4.3, 4.8)
  growth_rates["中部地区",] <- c(8.1, 7.5, 7.3, 6.4, 6.5, 5.6, 5.5, 6.1, 6.6)
  growth_rates["西部地区",] <- c(9.8, 9.0, 8.7, 8.3, 7.5, 7.3, 7.4, 7.8, 8.5)
  growth_rates["东北地区",] <- c(4.4, 4.3, 3.8, 3.4, 3.7, 3.1, 2.8, 2.5, 3.0)
  growth_rates["京津冀",] <- c(6.8, 5.4, 5.5, 4.3, 4.8, 4.1, 3.8, 3.6, 3.6)
  
  # 创建面板数据
  regional_data <- expand.grid(
    region_type = region_types,
    year = years
  )
  
  regional_data$gdp_growth <- sapply(1:nrow(regional_data), function(i) {
    rt <- regional_data$region_type[i]
    yr <- regional_data$year[i]
    return(growth_rates[rt, as.character(yr)])
  })
  
  # 添加失业率
  unemployment_base <- c(3.4, 3.8, 4.0, 4.8, 3.0)  # 基准失业率
  names(unemployment_base) <- region_types
  
  regional_data$unemployment_rate <- sapply(1:nrow(regional_data), function(i) {
    rt <- regional_data$region_type[i]
    yr <- regional_data$year[i]
    base <- unemployment_base[rt]
    
    # 关税战期间失业率上升
    if (yr >= 2018 && yr <= 2020) {
      # 沿海和东北受影响更大
      if (rt %in% c("沿海制造业", "东北地区")) {
        return(base + runif(1, 0.4, 0.8))
      } else {
        return(base + runif(1, 0.1, 0.4))
      }
    } else {
      return(base + runif(1, -0.2, 0.2))
    }
  })
  
  # 添加贸易依存度
  trade_dependency <- c(0.85, 0.5, 0.3, 0.4, 0.6)  # 基准贸易依存度
  names(trade_dependency) <- region_types
  
  regional_data$trade_dependency <- sapply(1:nrow(regional_data), function(i) {
    rt <- regional_data$region_type[i]
    return(trade_dependency[rt] + runif(1, -0.05, 0.05))
  })
  
  # 创建区域GDP增长率图
  regional_plot <- ggplot(regional_data, aes(x = year, y = gdp_growth, color = region_type, group = region_type)) +
    geom_line() +
    geom_point() +
    geom_vline(xintercept = 2018, linetype = "dashed", color = "red") +
    annotate("text", x = 2018, y = max(regional_data$gdp_growth), 
             label = "关税战开始", hjust = -0.2, color = "red") +
    labs(title = "不同区域类型GDP增长率变化 (2017-2025)",
         x = "年份", y = "平均GDP增长率 (%)", color = "区域类型") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  # 保存图表
  ggsave("figures/regional_growth.png", regional_plot, width = 10, height = 6)
  
  # 模拟回归分析结果
  model_coef <- data.frame(
    Estimate = c(-0.25, -0.42, 0.18, -1.35),
    `Std.Error` = c(0.12, 0.15, 0.08, 0.32),
    `t.value` = c(-2.08, -2.80, 2.25, -4.22),
    `Pr(>|t|)` = c(0.038, 0.005, 0.025, 0.000)
  )
  rownames(model_coef) <- c("失业率", "关税战后期", "贸易依存度", "关税战后期:贸易依存度")
  
  return(list(
    regional_data = regional_data,
    regional_plot = regional_plot,
    model_coef = model_coef
  ))
}

# 4. 创建战略资源数据
create_strategic_resources <- function() {
  # 生成月度时间序列
  dates <- seq(as.Date("2017-01-01"), as.Date("2025-04-01"), by = "month")
  n <- length(dates)
  
  # 模拟中国供应比例和美国依赖度
  china_supply <- c(
    rnorm(18, 59, 1),  # 关税前
    rnorm(18, 61, 1.5),  # 关税期间
    rnorm(64, 60, 1.2)   # 协议后
  )
  
  us_dependency <- c(
    rnorm(18, 74, 1),  # 关税前
    rnorm(18, 75, 1.5),  # 关税期间
    rnorm(64, 72, 2)   # 协议后
  )
  
  # 创建数据框
  resources_data <- data.frame(
    date = dates,
    avg_china_supply = pmin(pmax(china_supply, 55), 65),  # 限制在55-65范围内
    avg_us_dependency = pmin(pmax(us_dependency, 65), 80),  # 限制在65-80范围内
    tariff_period = ifelse(dates < as.Date("2018-07-06"), "关税战前",
                     ifelse(dates < as.Date("2020-01-15"), "关税战期间", "第一阶段协议后"))
  )
  
  # 创建资源依赖度图
  resources_plot <- ggplot(resources_data, aes(x = date)) +
    geom_line(aes(y = avg_china_supply, color = "中国稀土供应比例")) +
    geom_line(aes(y = avg_us_dependency, color = "美国稀土依赖度")) +
    geom_vline(xintercept = as.Date("2018-07-06"), linetype = "dashed", color = "red") +
    geom_vline(xintercept = as.Date("2020-01-15"), linetype = "dashed", color = "blue") +
    annotate("text", x = as.Date("2018-07-06"), y = max(resources_data$avg_us_dependency), 
             label = "首轮关税", hjust = -0.2, color = "red") +
    annotate("text", x = as.Date("2020-01-15"), y = max(resources_data$avg_us_dependency) * 0.95, 
             label = "第一阶段协议", hjust = -0.2, color = "blue") +
    scale_color_manual(values = c("中国稀土供应比例" = "red", "美国稀土依赖度" = "blue")) +
    labs(title = "稀土供应与依赖度变化 (2017-2025)",
         x = "日期", y = "百分比", color = "指标") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  # 保存图表
  ggsave("figures/strategic_resources.png", resources_plot, width = 10, height = 6)
  
  # 计算各时期平均值
  rare_earth_periods <- resources_data %>%
    group_by(tariff_period) %>%
    summarise(
      avg_china_supply = mean(avg_china_supply),
      avg_us_dependency = mean(avg_us_dependency),
      n = n()
    )
  
  return(list(
    resources_data = resources_data,
    rare_earth_periods = rare_earth_periods,
    resources_plot = resources_plot
  ))
}

# 整合所有分析结果
combine_results <- function() {
  tariff_analysis <- create_trade_data()
  sentiment_analysis <- create_sentiment_data()
  regional_analysis <- create_regional_data()
  strategic_analysis <- create_strategic_resources()
  
  results <- list(
    tariff_analysis = tariff_analysis,
    sentiment_analysis = sentiment_analysis,
    regional_analysis = regional_analysis,
    strategic_analysis = strategic_analysis
  )
  
  # 保存结果
  saveRDS(results, "analysis_results.rds")
  
  cat("模拟分析结果已生成并保存到 analysis_results.rds\n")
}

# 运行主程序
combine_results() 