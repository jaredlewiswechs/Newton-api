#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
STATSY VISUALIZATION & NEWTON INTEGRATION MODULE
═══════════════════════════════════════════════════════════════════════════════

ASCII visualizations and deep Newton integration for Statsy.

Features:
- ASCII charts: histogram, boxplot, scatter, sparkline, bar chart
- Robust statistics from Newton's core/robust.py
- Trust labels and verification
- Ledger integration for audit trails
- Constraint checking with CDL

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import math
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


# ═══════════════════════════════════════════════════════════════════════════════
# TRUST LABELS (from Newton's Trust Lattice)
# ═══════════════════════════════════════════════════════════════════════════════

class TrustLevel(Enum):
    """Trust levels for statistical values."""
    UNTRUSTED = 0    # Raw user input
    VERIFIED = 1     # Passed verification
    TRUSTED = 2      # From trusted source
    KERNEL = 3       # Core invariant (immutable)


@dataclass
class TrustedValue:
    """A value with trust label and verification trace."""
    value: Any
    trust: TrustLevel = TrustLevel.UNTRUSTED
    trace: List[str] = field(default_factory=list)
    verified_at: Optional[datetime] = None
    
    def upgrade(self, reason: str) -> 'TrustedValue':
        """Upgrade trust level with reason."""
        if self.trust.value < TrustLevel.TRUSTED.value:
            new_trust = TrustLevel(self.trust.value + 1)
            new_trace = self.trace + [f"[{datetime.now().isoformat()}] {reason}"]
            return TrustedValue(self.value, new_trust, new_trace, datetime.now())
        return self
    
    def __repr__(self):
        symbols = {
            TrustLevel.UNTRUSTED: "⚠️",
            TrustLevel.VERIFIED: "✓",
            TrustLevel.TRUSTED: "✓✓",
            TrustLevel.KERNEL: "🔒"
        }
        return f"{self.value} {symbols[self.trust]}"


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII VISUALIZATION CHARACTERS
# ═══════════════════════════════════════════════════════════════════════════════

# Histogram/bar characters
BLOCK_FULL = '█'
BLOCK_7_8 = '▉'
BLOCK_3_4 = '▊'
BLOCK_5_8 = '▋'
BLOCK_1_2 = '▌'
BLOCK_3_8 = '▍'
BLOCK_1_4 = '▎'
BLOCK_1_8 = '▏'
BLOCK_EMPTY = '░'

# Sparkline characters (8 levels)
SPARK_CHARS = '▁▂▃▄▅▆▇█'

# Box plot characters
BOX_H = '─'
BOX_V = '│'
BOX_TL = '┌'
BOX_TR = '┐'
BOX_BL = '└'
BOX_BR = '┘'
BOX_T = '┬'
BOX_B = '┴'
BOX_L = '├'
BOX_R = '┤'
BOX_X = '┼'

# Scatter plot characters
SCATTER_CHARS = ' ·∘○●'


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII HISTOGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def histogram(values: List[float], bins: int = 10, width: int = 40, 
              title: str = "Histogram", show_stats: bool = True) -> str:
    """
    Generate an ASCII histogram.
    
    Args:
        values: List of numeric values
        bins: Number of bins
        width: Width of the bars
        title: Chart title
        show_stats: Whether to show summary statistics
    
    Returns:
        ASCII histogram string
    """
    if not values:
        return "No data to display"
    
    # Filter NA values
    clean_vals = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if not clean_vals:
        return "No valid data to display"
    
    # Calculate histogram bins
    min_val = min(clean_vals)
    max_val = max(clean_vals)
    
    if min_val == max_val:
        # All values are the same
        counts = [len(clean_vals)]
        edges = [min_val, max_val]
    else:
        bin_width = (max_val - min_val) / bins
        edges = [min_val + i * bin_width for i in range(bins + 1)]
        counts = [0] * bins
        
        for v in clean_vals:
            idx = min(int((v - min_val) / bin_width), bins - 1)
            counts[idx] += 1
    
    max_count = max(counts) if counts else 1
    
    # Build output
    lines = []
    lines.append(f"┌{'─' * (width + 20)}┐")
    lines.append(f"│ {title:^{width + 18}} │")
    lines.append(f"├{'─' * (width + 20)}┤")
    
    for i, count in enumerate(counts):
        bar_len = int(count / max_count * width) if max_count > 0 else 0
        bar = BLOCK_FULL * bar_len + BLOCK_EMPTY * (width - bar_len)
        if len(edges) > i:
            lines.append(f"│ {edges[i]:7.2f} │{bar}│ {count:4} │")
    
    lines.append(f"└{'─' * (width + 20)}┘")
    
    # Add statistics
    if show_stats:
        n = len(clean_vals)
        mean = sum(clean_vals) / n
        variance = sum((x - mean) ** 2 for x in clean_vals) / (n - 1) if n > 1 else 0
        std = math.sqrt(variance)
        median = sorted(clean_vals)[n // 2]
        
        lines.append(f"  n={n} | mean={mean:.2f} | std={std:.2f} | median={median:.2f}")
    
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII BOXPLOT
# ═══════════════════════════════════════════════════════════════════════════════

def boxplot(values: List[float], width: int = 50, title: str = "Box Plot") -> str:
    """
    Generate an ASCII box plot.
    
    Displays: min ──┤ Q1 ████ median ████ Q3 ├── max
    """
    if not values:
        return "No data to display"
    
    clean_vals = sorted([v for v in values if v is not None])
    if not clean_vals:
        return "No valid data to display"
    
    n = len(clean_vals)
    min_val = clean_vals[0]
    max_val = clean_vals[-1]
    q1 = clean_vals[n // 4]
    median = clean_vals[n // 2]
    q3 = clean_vals[3 * n // 4]
    
    # Calculate positions (normalize to width)
    range_val = max_val - min_val
    if range_val == 0:
        range_val = 1
    
    def pos(v):
        return int((v - min_val) / range_val * (width - 1))
    
    pos_min = 0
    pos_q1 = pos(q1)
    pos_med = pos(median)
    pos_q3 = pos(q3)
    pos_max = width - 1
    
    # Build the plot
    lines = []
    lines.append(f"┌{'─' * (width + 4)}┐")
    lines.append(f"│ {title:^{width + 2}} │")
    lines.append(f"├{'─' * (width + 4)}┤")
    
    # Main box plot line
    plot = [' '] * width
    
    # Draw whiskers
    for i in range(pos_min, pos_q1):
        plot[i] = '─'
    for i in range(pos_q3, pos_max + 1):
        plot[i] = '─'
    
    # Draw box
    for i in range(pos_q1, pos_q3 + 1):
        plot[i] = '█'
    
    # Draw median
    if 0 <= pos_med < width:
        plot[pos_med] = '│'
    
    # Draw endpoints
    plot[pos_min] = '├'
    plot[pos_max] = '┤'
    
    lines.append(f"│  {''.join(plot)}  │")
    
    # Scale line
    scale = f"{min_val:.1f}" + ' ' * (width - len(f"{min_val:.1f}") - len(f"{max_val:.1f}")) + f"{max_val:.1f}"
    lines.append(f"│  {scale}  │")
    
    lines.append(f"├{'─' * (width + 4)}┤")
    lines.append(f"│ Min={min_val:.2f} Q1={q1:.2f} Med={median:.2f} Q3={q3:.2f} Max={max_val:.2f} │")
    lines.append(f"│ IQR={q3-q1:.2f}  │")
    lines.append(f"└{'─' * (width + 4)}┘")
    
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII SPARKLINE
# ═══════════════════════════════════════════════════════════════════════════════

def sparkline(values: List[float], label: str = "") -> str:
    """
    Generate a sparkline (mini inline chart).
    
    Uses characters: ▁▂▃▄▅▆▇█
    """
    if not values:
        return "▁" * 10
    
    clean_vals = [v for v in values if v is not None]
    if not clean_vals:
        return "▁" * 10
    
    min_val = min(clean_vals)
    max_val = max(clean_vals)
    range_val = max_val - min_val
    
    if range_val == 0:
        return SPARK_CHARS[4] * len(clean_vals)
    
    result = []
    for v in clean_vals:
        idx = int((v - min_val) / range_val * 7)
        idx = max(0, min(7, idx))
        result.append(SPARK_CHARS[idx])
    
    spark = ''.join(result)
    
    if label:
        return f"{label}: {spark} [{min_val:.1f}-{max_val:.1f}]"
    return spark


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII SCATTER PLOT
# ═══════════════════════════════════════════════════════════════════════════════

def scatter(x_vals: List[float], y_vals: List[float], 
            width: int = 60, height: int = 20,
            title: str = "Scatter Plot",
            x_label: str = "x", y_label: str = "y") -> str:
    """
    Generate an ASCII scatter plot.
    """
    if not x_vals or not y_vals:
        return "No data to display"
    
    # Pair and filter
    pairs = [(x, y) for x, y in zip(x_vals, y_vals) 
             if x is not None and y is not None]
    if not pairs:
        return "No valid data pairs"
    
    x_vals = [p[0] for p in pairs]
    y_vals = [p[1] for p in pairs]
    
    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)
    
    x_range = x_max - x_min or 1
    y_range = y_max - y_min or 1
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Plot points
    for x, y in pairs:
        col = int((x - x_min) / x_range * (width - 1))
        row = int((y_max - y) / y_range * (height - 1))  # Invert y
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        
        # Increase intensity for overlapping points
        current = grid[row][col]
        if current == ' ':
            grid[row][col] = '·'
        elif current == '·':
            grid[row][col] = '∘'
        elif current == '∘':
            grid[row][col] = '○'
        elif current == '○':
            grid[row][col] = '●'
    
    # Build output
    lines = []
    lines.append(f"┌{'─' * (width + 10)}┐")
    lines.append(f"│ {title:^{width + 8}} │")
    lines.append(f"├{'─' * (width + 10)}┤")
    
    for i, row in enumerate(grid):
        y_val = y_max - (i / (height - 1)) * y_range if height > 1 else y_max
        lines.append(f"│ {y_val:7.2f} │{''.join(row)}│")
    
    # X axis
    lines.append(f"│         └{'─' * width}┘")
    x_scale = f"{x_min:.1f}" + ' ' * (width - 12) + f"{x_max:.1f}"
    lines.append(f"│          {x_scale}")
    lines.append(f"│          {x_label:^{width}}")
    lines.append(f"└{'─' * (width + 10)}┘")
    
    # Add correlation
    n = len(pairs)
    if n > 2:
        mx = sum(x_vals) / n
        my = sum(y_vals) / n
        num = sum((x - mx) * (y - my) for x, y in pairs)
        denom_x = math.sqrt(sum((x - mx) ** 2 for x in x_vals))
        denom_y = math.sqrt(sum((y - my) ** 2 for y in y_vals))
        r = num / (denom_x * denom_y) if denom_x > 0 and denom_y > 0 else 0
        lines.append(f"  n={n} | r={r:.4f}")
    
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII BAR CHART
# ═══════════════════════════════════════════════════════════════════════════════

def bar_chart(labels: List[str], values: List[float], 
              width: int = 40, title: str = "Bar Chart") -> str:
    """
    Generate an ASCII horizontal bar chart.
    """
    if not labels or not values:
        return "No data to display"
    
    max_val = max(values) if values else 1
    max_label_len = max(len(str(l)) for l in labels)
    
    lines = []
    lines.append(f"┌{'─' * (max_label_len + width + 15)}┐")
    lines.append(f"│ {title:^{max_label_len + width + 13}} │")
    lines.append(f"├{'─' * (max_label_len + width + 15)}┤")
    
    for label, val in zip(labels, values):
        bar_len = int(val / max_val * width) if max_val > 0 else 0
        bar = BLOCK_FULL * bar_len + BLOCK_EMPTY * (width - bar_len)
        lines.append(f"│ {str(label):>{max_label_len}} │{bar}│ {val:8.2f} │")
    
    lines.append(f"└{'─' * (max_label_len + width + 15)}┘")
    
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII LINE CHART
# ═══════════════════════════════════════════════════════════════════════════════

def line_chart(values: List[float], width: int = 60, height: int = 15,
               title: str = "Line Chart", show_trend: bool = True) -> str:
    """
    Generate an ASCII line chart with optional trend line.
    """
    if not values:
        return "No data to display"
    
    clean_vals = [v for v in values if v is not None]
    if not clean_vals:
        return "No valid data"
    
    n = len(clean_vals)
    min_val = min(clean_vals)
    max_val = max(clean_vals)
    range_val = max_val - min_val or 1
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Plot points and connect
    prev_row = None
    for i, v in enumerate(clean_vals):
        col = int(i / (n - 1) * (width - 1)) if n > 1 else 0
        row = int((max_val - v) / range_val * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        
        grid[row][col] = '●'
        
        # Connect to previous point
        if prev_row is not None:
            prev_col = int((i - 1) / (n - 1) * (width - 1)) if n > 1 else 0
            # Simple line connection
            for c in range(min(prev_col, col) + 1, max(prev_col, col)):
                # Interpolate row
                frac = (c - prev_col) / (col - prev_col) if col != prev_col else 0
                interp_row = int(prev_row + frac * (row - prev_row))
                interp_row = max(0, min(height - 1, interp_row))
                if grid[interp_row][c] == ' ':
                    grid[interp_row][c] = '─'
        
        prev_row = row
    
    # Build output
    lines = []
    lines.append(f"┌{'─' * (width + 10)}┐")
    lines.append(f"│ {title:^{width + 8}} │")
    lines.append(f"├{'─' * (width + 10)}┤")
    
    for i, row in enumerate(grid):
        y_val = max_val - (i / (height - 1)) * range_val if height > 1 else max_val
        lines.append(f"│ {y_val:7.2f} │{''.join(row)}│")
    
    lines.append(f"└{'─' * (width + 10)}┘")
    
    # Add sparkline summary
    lines.append(f"  Trend: {sparkline(clean_vals)}")
    
    # Add statistics
    mean = sum(clean_vals) / n
    lines.append(f"  n={n} | min={min_val:.2f} | max={max_val:.2f} | mean={mean:.2f}")
    
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# ROBUST STATISTICS (Newton-style: MAD over Mean)
# ═══════════════════════════════════════════════════════════════════════════════

def mad(values: List[float]) -> float:
    """
    Median Absolute Deviation - robust measure of dispersion.
    
    MAD = median(|x_i - median(x)|) * 1.4826
    
    The 1.4826 scaling factor makes MAD comparable to std dev for normal dist.
    """
    if not values:
        return float('nan')
    
    clean = [v for v in values if v is not None]
    if not clean:
        return float('nan')
    
    med = sorted(clean)[len(clean) // 2]
    deviations = [abs(v - med) for v in clean]
    mad_value = sorted(deviations)[len(deviations) // 2]
    
    return mad_value * 1.4826  # Scale factor for normal distribution


def modified_zscore(values: List[float]) -> List[float]:
    """
    Modified Z-score using median and MAD (robust to outliers).
    
    M_i = 0.6745 * (x_i - median) / MAD
    """
    if not values:
        return []
    
    clean = [v for v in values if v is not None]
    if not clean:
        return []
    
    med = sorted(clean)[len(clean) // 2]
    mad_val = mad(clean) / 1.4826  # Unscaled MAD
    
    if mad_val == 0:
        return [0.0] * len(clean)
    
    return [0.6745 * (v - med) / mad_val for v in clean]


def is_outlier(value: float, values: List[float], threshold: float = 3.5) -> bool:
    """
    Detect outlier using modified Z-score.
    
    A value is an outlier if |M_i| > threshold (default 3.5).
    """
    clean = [v for v in values if v is not None]
    if not clean:
        return False
    
    med = sorted(clean)[len(clean) // 2]
    mad_val = mad(clean) / 1.4826
    
    if mad_val == 0:
        return False
    
    m_score = abs(0.6745 * (value - med) / mad_val)
    return m_score > threshold


def detect_outliers(values: List[float], threshold: float = 3.5) -> List[Tuple[int, float]]:
    """
    Detect all outliers in a dataset.
    
    Returns list of (index, value) tuples for outliers.
    """
    outliers = []
    for i, v in enumerate(values):
        if v is not None and is_outlier(v, values, threshold):
            outliers.append((i, v))
    return outliers


def trimmed_mean(values: List[float], trim: float = 0.1) -> float:
    """
    Trimmed mean - removes extreme values before averaging.
    
    Args:
        values: List of values
        trim: Proportion to trim from each end (0.1 = 10% from each end)
    """
    if not values:
        return float('nan')
    
    clean = sorted([v for v in values if v is not None])
    if not clean:
        return float('nan')
    
    n = len(clean)
    k = int(n * trim)
    
    if 2 * k >= n:
        # Too much trimming, return median
        return clean[n // 2]
    
    trimmed = clean[k:n-k]
    return sum(trimmed) / len(trimmed)


def winsorized_mean(values: List[float], trim: float = 0.1) -> float:
    """
    Winsorized mean - replaces extreme values instead of removing.
    """
    if not values:
        return float('nan')
    
    clean = sorted([v for v in values if v is not None])
    if not clean:
        return float('nan')
    
    n = len(clean)
    k = int(n * trim)
    
    if k == 0:
        return sum(clean) / n
    
    # Replace extremes with boundary values
    lower = clean[k]
    upper = clean[n - k - 1]
    
    winsorized = [max(lower, min(upper, v)) for v in clean]
    return sum(winsorized) / len(winsorized)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT CHECKING (Newton CDL-style)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Constraint:
    """A statistical constraint to verify."""
    name: str
    check: Callable[[Any], bool]
    message: str


def verify_constraints(value: Any, constraints: List[Constraint]) -> Tuple[bool, List[str]]:
    """
    Verify value against constraints.
    
    Returns (all_passed, list_of_failures).
    """
    failures = []
    
    for c in constraints:
        if not c.check(value):
            failures.append(f"❌ {c.name}: {c.message}")
    
    return len(failures) == 0, failures


# Common statistical constraints
def constraint_positive(x) -> bool:
    """Value must be positive."""
    if hasattr(x, '__iter__'):
        return all(v > 0 for v in x if v is not None)
    return x > 0

def constraint_non_negative(x) -> bool:
    """Value must be non-negative."""
    if hasattr(x, '__iter__'):
        return all(v >= 0 for v in x if v is not None)
    return x >= 0

def constraint_probability(x) -> bool:
    """Value must be between 0 and 1."""
    if hasattr(x, '__iter__'):
        return all(0 <= v <= 1 for v in x if v is not None)
    return 0 <= x <= 1

def constraint_no_na(x) -> bool:
    """No missing values allowed."""
    if hasattr(x, '__iter__'):
        return all(v is not None for v in x)
    return x is not None

def constraint_finite(x) -> bool:
    """Value must be finite."""
    if hasattr(x, '__iter__'):
        return all(math.isfinite(v) for v in x if v is not None)
    return math.isfinite(x)


COMMON_CONSTRAINTS = {
    'positive': Constraint('positive', constraint_positive, "Values must be positive"),
    'non_negative': Constraint('non_negative', constraint_non_negative, "Values must be non-negative"),
    'probability': Constraint('probability', constraint_probability, "Values must be between 0 and 1"),
    'no_na': Constraint('no_na', constraint_no_na, "No missing values allowed"),
    'finite': Constraint('finite', constraint_finite, "Values must be finite"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT TRAIL (Newton Ledger-style)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AuditEntry:
    """An entry in the computation audit trail."""
    index: int
    timestamp: datetime
    operation: str
    input_hash: str
    result_hash: str
    verified: bool
    
    def __repr__(self):
        status = "✓" if self.verified else "✗"
        return f"[{self.index}] {self.timestamp.isoformat()} | {self.operation} | {status}"


class AuditTrail:
    """Immutable audit trail for statistical computations."""
    
    def __init__(self):
        self.entries: List[AuditEntry] = []
        self._index = 0
    
    def log(self, operation: str, input_data: Any, result: Any, verified: bool = True) -> AuditEntry:
        """Log a computation to the audit trail."""
        entry = AuditEntry(
            index=self._index,
            timestamp=datetime.now(),
            operation=operation,
            input_hash=hashlib.sha256(str(input_data).encode()).hexdigest()[:16],
            result_hash=hashlib.sha256(str(result).encode()).hexdigest()[:16],
            verified=verified
        )
        self.entries.append(entry)
        self._index += 1
        return entry
    
    def show(self, last_n: int = 10) -> str:
        """Show recent audit entries."""
        lines = []
        lines.append("┌─────────────────────────────────────────────────────────────┐")
        lines.append("│ AUDIT TRAIL                                                 │")
        lines.append("├─────────────────────────────────────────────────────────────┤")
        
        for entry in self.entries[-last_n:]:
            status = "✓" if entry.verified else "✗"
            lines.append(f"│ [{entry.index:3}] {entry.operation:20} {status} │")
        
        lines.append("└─────────────────────────────────────────────────────────────┘")
        return '\n'.join(lines)


# Global audit trail
_audit_trail = AuditTrail()

def get_audit_trail() -> AuditTrail:
    """Get the global audit trail."""
    return _audit_trail


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def load_csv(filepath: str, has_header: bool = True) -> Dict[str, List[Any]]:
    """
    Load a CSV file into a dictionary of columns.
    """
    import csv
    
    data = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        if has_header:
            headers = next(reader)
        else:
            # Peek first row for column count
            first_row = next(reader)
            headers = [f"col_{i}" for i in range(len(first_row))]
            # Re-read with this row
            f.seek(0)
            reader = csv.reader(f)
        
        # Initialize columns
        for h in headers:
            data[h] = []
        
        # Read data
        for row in reader:
            for i, val in enumerate(row):
                if i < len(headers):
                    # Try to convert to number
                    try:
                        data[headers[i]].append(float(val))
                    except ValueError:
                        if val.lower() in ('', 'na', 'nan', 'null', 'none'):
                            data[headers[i]].append(None)
                        else:
                            data[headers[i]].append(val)
    
    return data


def load_json(filepath: str) -> Any:
    """Load a JSON file."""
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════════════════
# REGRESSION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LinearModel:
    """Result of linear regression."""
    intercept: float
    slope: float
    r_squared: float
    residuals: List[float]
    n: int
    
    def predict(self, x: Union[float, List[float]]) -> Union[float, List[float]]:
        """Predict y for given x."""
        if isinstance(x, list):
            return [self.intercept + self.slope * xi for xi in x]
        return self.intercept + self.slope * x
    
    def __repr__(self):
        return f"y = {self.intercept:.4f} + {self.slope:.4f}x (R² = {self.r_squared:.4f})"


def linear_regression(x: List[float], y: List[float]) -> LinearModel:
    """
    Simple linear regression: y = a + bx
    """
    pairs = [(xi, yi) for xi, yi in zip(x, y) if xi is not None and yi is not None]
    if len(pairs) < 2:
        raise ValueError("Need at least 2 data points")
    
    x_vals = [p[0] for p in pairs]
    y_vals = [p[1] for p in pairs]
    n = len(pairs)
    
    # Calculate means
    x_mean = sum(x_vals) / n
    y_mean = sum(y_vals) / n
    
    # Calculate slope and intercept
    num = sum((x - x_mean) * (y - y_mean) for x, y in pairs)
    denom = sum((x - x_mean) ** 2 for x in x_vals)
    
    if denom == 0:
        raise ValueError("X values have zero variance")
    
    slope = num / denom
    intercept = y_mean - slope * x_mean
    
    # Calculate R-squared
    y_pred = [intercept + slope * x for x in x_vals]
    ss_res = sum((y - yp) ** 2 for y, yp in zip(y_vals, y_pred))
    ss_tot = sum((y - y_mean) ** 2 for y in y_vals)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    
    # Residuals
    residuals = [y - yp for y, yp in zip(y_vals, y_pred)]
    
    return LinearModel(intercept, slope, r_squared, residuals, n)


# ═══════════════════════════════════════════════════════════════════════════════
# ANOVA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ANOVAResult:
    """Result of one-way ANOVA."""
    f_statistic: float
    p_value: float
    df_between: int
    df_within: int
    ss_between: float
    ss_within: float
    group_means: List[float]
    
    def __repr__(self):
        sig = "***" if self.p_value < 0.001 else "**" if self.p_value < 0.01 else "*" if self.p_value < 0.05 else ""
        return f"F({self.df_between},{self.df_within}) = {self.f_statistic:.4f}, p = {self.p_value:.4f} {sig}"


def one_way_anova(*groups: List[float]) -> ANOVAResult:
    """
    One-way ANOVA for comparing means of multiple groups.
    """
    if len(groups) < 2:
        raise ValueError("Need at least 2 groups")
    
    # Clean groups
    clean_groups = [[v for v in g if v is not None] for g in groups]
    
    k = len(clean_groups)  # Number of groups
    n_total = sum(len(g) for g in clean_groups)
    
    # Group means and sizes
    group_means = [sum(g) / len(g) for g in clean_groups]
    group_sizes = [len(g) for g in clean_groups]
    
    # Grand mean
    grand_mean = sum(sum(g) for g in clean_groups) / n_total
    
    # Sum of squares
    ss_between = sum(n * (m - grand_mean) ** 2 for n, m in zip(group_sizes, group_means))
    ss_within = sum(sum((x - m) ** 2 for x in g) for g, m in zip(clean_groups, group_means))
    
    # Degrees of freedom
    df_between = k - 1
    df_within = n_total - k
    
    # Mean squares
    ms_between = ss_between / df_between if df_between > 0 else 0
    ms_within = ss_within / df_within if df_within > 0 else 0
    
    # F statistic
    f_stat = ms_between / ms_within if ms_within > 0 else float('inf')
    
    # Approximate p-value (using normal approximation for simplicity)
    # For a proper implementation, use scipy.stats.f.sf
    p_value = 2 * (1 - 0.5 * (1 + math.erf(f_stat / math.sqrt(2))))  # Very rough approximation
    
    return ANOVAResult(f_stat, p_value, df_between, df_within, ss_between, ss_within, group_means)


# ═══════════════════════════════════════════════════════════════════════════════
# TIME SERIES
# ═══════════════════════════════════════════════════════════════════════════════

def moving_average(values: List[float], window: int = 3) -> List[Optional[float]]:
    """
    Calculate moving average.
    """
    if not values or window < 1:
        return []
    
    result = [None] * (window - 1)  # Padding at start
    
    for i in range(window - 1, len(values)):
        window_vals = [v for v in values[i - window + 1:i + 1] if v is not None]
        if window_vals:
            result.append(sum(window_vals) / len(window_vals))
        else:
            result.append(None)
    
    return result


def exponential_smoothing(values: List[float], alpha: float = 0.3) -> List[float]:
    """
    Exponential smoothing for time series.
    
    S_t = alpha * x_t + (1 - alpha) * S_{t-1}
    """
    if not values:
        return []
    
    clean = [v for v in values if v is not None]
    if not clean:
        return []
    
    result = [clean[0]]  # First value as initial
    
    for v in clean[1:]:
        result.append(alpha * v + (1 - alpha) * result[-1])
    
    return result


def trend_decomposition(values: List[float], window: int = 3) -> Dict[str, List[float]]:
    """
    Simple trend decomposition: original = trend + seasonal + residual
    """
    trend = moving_average(values, window)
    
    # For simplicity, seasonal is assumed 0, residual is original - trend
    residual = []
    for v, t in zip(values, trend):
        if v is not None and t is not None:
            residual.append(v - t)
        else:
            residual.append(None)
    
    return {
        'original': values,
        'trend': trend,
        'residual': residual
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PRETTY OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

def verified_output(value: Any, operation: str, verified: bool = True) -> str:
    """Format output with verification status."""
    status = "✓ VERIFIED" if verified else "⚠️ UNVERIFIED"
    
    lines = []
    lines.append(f"┌─────────────────────────────────────────────────────────────┐")
    lines.append(f"│ {operation:^59} │")
    lines.append(f"├─────────────────────────────────────────────────────────────┤")
    lines.append(f"│ Result: {str(value)[:50]:50} │")
    lines.append(f"│ Status: {status:50} │")
    lines.append(f"│ Time: {datetime.now().isoformat()[:19]:50} │")
    lines.append(f"└─────────────────────────────────────────────────────────────┘")
    
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# NEWTON KNOWLEDGE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

_newton_kb = None

def get_newton_kb():
    """Lazy-load Newton knowledge base."""
    global _newton_kb
    if _newton_kb is not None:
        return _newton_kb
    
    try:
        import sys
        import os
        # Find Newton-api root
        current = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(current)
        sys.path.insert(0, root)
        
        from adan.knowledge_base import get_knowledge_base
        _newton_kb = get_knowledge_base()
    except ImportError:
        _newton_kb = None
    
    return _newton_kb


def newton_ask(question: str) -> str:
    """Query Newton knowledge base."""
    kb = get_newton_kb()
    if kb is None:
        return "Newton KB not available"
    
    result = kb.query(question)
    if result:
        return f"📚 {result.fact}\n   Source: {result.source}"
    return "No answer found"


def newton_verify(claim: str) -> bool:
    """Verify a claim through Newton."""
    kb = get_newton_kb()
    if kb is None:
        return False
    
    result = kb.query(claim)
    return result is not None


def statistical_guidance(topic: str) -> str:
    """Get Newton's guidance on a statistical topic."""
    questions = [
        f"What is {topic}?",
        f"How to interpret {topic}?",
        f"When to use {topic}?",
    ]
    
    kb = get_newton_kb()
    if kb is None:
        return "Newton KB not available for guidance"
    
    lines = []
    lines.append(f"═══ Statistical Guidance: {topic} ═══")
    
    for q in questions:
        result = kb.query(q)
        if result:
            lines.append(f"\n{q}")
            lines.append(f"  {result.fact[:200]}...")
            break
    
    if len(lines) == 1:
        lines.append(f"\nNo guidance found for '{topic}'")
    
    return '\n'.join(lines)
