# ===========================================================================
# STATSY VISUALIZATION EXAMPLES
# ASCII charts, advanced statistics, and Newton integration
# ===========================================================================

print("===================================================================")
print("  STATSY: The Dream Statistical Language - Visualization Demo")
print("===================================================================")

# ---------------------------------------------------------------------------
# SAMPLE DATA
# ---------------------------------------------------------------------------

# Normal-ish data with some variation
heights = [165, 170, 168, 172, 175, 169, 171, 167, 174, 173, 168, 166, 170, 172, 169, 171, 168, 175, 167, 170]

# Data with outliers
sales = [100, 105, 98, 102, 110, 95, 108, 500, 103, 99, 107, 101, 96, 104, 98, 102, 600, 97, 105, 103]

# Time series data (monthly values)
monthly = [45, 48, 52, 55, 58, 62, 68, 72, 70, 65, 58, 50]

# Group data for ANOVA
group_a = [23, 25, 27, 22, 24, 26, 28, 23, 25, 27]
group_b = [30, 32, 28, 35, 31, 33, 29, 34, 30, 32]
group_c = [18, 20, 22, 19, 21, 17, 23, 20, 18, 22]

print("")
print("Sample datasets loaded:")
print("  - heights: 20 measurements")
print("  - sales: 20 values with outliers")
print("  - monthly: 12 time points")
print("  - group_a, group_b, group_c: for ANOVA")
print("")

# ---------------------------------------------------------------------------
# 1. HISTOGRAM
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  1. HISTOGRAM - Distribution of Heights")
print("==================================================================")
print("")

histogram(heights, 8, 35, "Height Distribution (cm)")

# ---------------------------------------------------------------------------
# 2. BOXPLOT
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  2. BOXPLOT - Heights Summary")
print("==================================================================")
print("")

boxplot(heights, 50, "Height Box Plot")

# ---------------------------------------------------------------------------
# 3. SPARKLINE - Inline Mini Charts
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  3. SPARKLINES - Compact Trend Display")
print("==================================================================")
print("")

print(sparkline(monthly, "Monthly Trend"))
print(sparkline(sales, "Sales (with outliers)"))
print(sparkline(heights, "Heights"))

# ---------------------------------------------------------------------------
# 4. LINE CHART - Time Series
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  4. LINE CHART - Monthly Data")
print("==================================================================")
print("")

line_chart(monthly, 50, 12, "Monthly Values Over Time")

# ---------------------------------------------------------------------------
# 5. OUTLIER DETECTION (Newton Robust Statistics)
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  5. OUTLIER DETECTION - Modified Z-Score (MAD-based)")
print("==================================================================")
print("")

print("Sales data with outliers:")
describe(sales)

outliers = detect_outliers(sales, 3.5)
print("")
print("Detected outliers:")
print(outliers)

print("")
print("Robust alternatives:")
reg_mean = mean(sales)
trim_mean = trimmed_mean(sales, 0.1)
win_mean = winsorized_mean(sales, 0.1)
rob_mean = robust_mean(sales)

print("  Regular mean:    ")
print(reg_mean)
print("  Trimmed mean:    ")
print(trim_mean)
print("  Winsorized mean: ")
print(win_mean)
print("  Robust mean:     ")
print(rob_mean)

# ---------------------------------------------------------------------------
# 6. LINEAR REGRESSION
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  6. LINEAR REGRESSION")
print("==================================================================")
print("")

# Create x,y data with linear relationship
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y = [2.1, 4.0, 5.8, 8.2, 9.9, 12.1, 14.0, 16.2, 17.8, 20.1]

print("Data: y ~ 2x")
model = lm(x, y)

print("")
print("Scatter plot of data:")
scatter(x, y, 50, 15, "X vs Y Relationship")

# ---------------------------------------------------------------------------
# 7. ONE-WAY ANOVA
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  7. ONE-WAY ANOVA - Comparing Groups")
print("==================================================================")
print("")

print("Group means:")
ma = mean(group_a)
mb = mean(group_b)
mc = mean(group_c)
print("  Group A: ")
print(ma)
print("  Group B: ")
print(mb)
print("  Group C: ")
print(mc)
print("")

result = anova(group_a, group_b, group_c)

# ---------------------------------------------------------------------------
# 8. TIME SERIES ANALYSIS
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  8. TIME SERIES - Smoothing Methods")
print("==================================================================")
print("")

noisy = [10, 12, 8, 15, 11, 18, 14, 20, 16, 22, 18, 25]

s1 = sparkline(noisy, "Raw")
s2 = sparkline(moving_avg(noisy, 3), "Moving Avg")
s3 = sparkline(exp_smooth(noisy, 0.3), "Exp Smooth")

print("Original: ")
print(s1)
print("MA(3):    ")
print(s2)
print("Exp(0.3): ")
print(s3)

# ---------------------------------------------------------------------------
# 9. BAR CHART
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  9. BAR CHART - Category Comparison")
print("==================================================================")
print("")

categories = ["Q1", "Q2", "Q3", "Q4"]
vals = [125, 180, 165, 210]

bar_chart(categories, vals, 35, "Quarterly Revenue")

# ---------------------------------------------------------------------------
# 10. NEWTON INTEGRATION - Statistical Guidance
# ---------------------------------------------------------------------------

print("")
print("==================================================================")
print("  10. NEWTON INTEGRATION - Verified Knowledge")
print("==================================================================")
print("")

# Get guidance on statistical topics
guidance("t-test")

print("")
newton_ask("What is standard deviation?")

print("")
print("===================================================================")
print("  Demo complete! Statsy: Statistics you can trust.")
print("===================================================================")
