# Statsy Quick Reference

## Run Statsy
```bash
# Interactive REPL
python statsy/statsy.py

# Run a script
python statsy/statsy.py script.st
```

## Basic Syntax
```statsy
# Variables
x = 42
name = "Alice"
flag = true

# Vectors
data = [1, 2, 3, 4, 5]

# Operations
y = x + 10
z = data * 2
result = data |> mean()
```

## Descriptive Statistics
```statsy
mean(x)      # Arithmetic mean
median(x)    # Median
mode(x)      # Mode
std(x)       # Standard deviation
var(x)       # Variance
sum(x)       # Sum
min(x)       # Minimum
max(x)       # Maximum
range(x)     # [min, max]
quantile(x, p) # p-th quantile
iqr(x)       # Interquartile range

# Robust statistics (Newton-style)
mad(x)       # Median Absolute Deviation
robust_mean(x) # Trimmed mean
describe(x)  # Full summary with outlier detection
```

## Statistical Tests
```statsy
t_test(x, y)    # Two-sample t-test
cor(x, y)       # Correlation coefficient
cor_test(x, y)  # Correlation test
```

## Distributions
```statsy
dnorm(x, mu, sigma)  # Normal PDF
pnorm(x, mu, sigma)  # Normal CDF
qnorm(p, mu, sigma)  # Normal quantile
rnorm(n, mu, sigma)  # Random normal sample
```

## Control Flow
```statsy
# Conditionals
if condition {
    # ...
} else {
    # ...
}

# Loops
for item in data {
    # ...
}
```

## Functions
```statsy
fn my_function(a, b) {
    result = a + b
    return result
}

# Call it
my_function(1, 2)
```

## Newton Integration
```statsy
# Query knowledge base
newton_ask("What is standard deviation?")

# Verify a claim
newton_verify("The mean is sensitive to outliers")

# Statistical guidance
guidance("t-test")
```

## ASCII Visualizations
```statsy
# Histogram
histogram(data, 10, 40, "Title")

# Box plot
boxplot(data, 50, "Title")

# Sparkline (inline)
sparkline(data, "Label")   # -> ▁▂▃▅▇█

# Scatter plot
scatter(x, y, 60, 20, "Title")

# Line chart
line_chart(data, 50, 15, "Title")

# Bar chart
bar_chart(labels, values, 40, "Title")
```

## Advanced Statistics
```statsy
# Linear regression
model = lm(x, y)

# ANOVA
anova(group1, group2, group3)

# Robust statistics
modified_zscore(data)
detect_outliers(data, 3.5)
trimmed_mean(data, 0.1)
winsorized_mean(data, 0.1)

# Time series
moving_avg(data, 3)
exp_smooth(data, 0.3)
```

## Data Loading
```statsy
data = load_csv("file.csv", true)
config = load_json("config.json")
```

## Pipe Operator
```statsy
# Fluent style
data |> mean()
data |> std()
[1, 2, 3, 100] |> mad()
```

## Special Values
```statsy
NA           # Missing value
true / false # Booleans
```

---
© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
