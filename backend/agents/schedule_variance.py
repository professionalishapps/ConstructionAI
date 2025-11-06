"""Agent 1: Schedule Variance Analyzer (simple implementation)
Calculates a simplified Schedule Performance Index (SPI) and days ahead/behind schedule.
"""
from decimal import Decimal


def calculate_spi(baseline_pct_complete: float, actual_pct_complete: float) -> float:
    """Simplified SPI: ratio of actual to planned percent complete.
    If planned percent is zero, returns 1.0.
    """
    if baseline_pct_complete == 0:
        return 1.0
    try:
        spi = actual_pct_complete / baseline_pct_complete
    except Exception:
        spi = 1.0
    return round(spi, 3)


def days_ahead_behind(baseline_pct_complete: float, actual_pct_complete: float, total_days: int) -> int:
    """Estimate days ahead/behind based on percent complete gap and total_days.
    Positive means ahead, negative means behind.
    """
    try:
        pct_gap = actual_pct_complete - baseline_pct_complete
        # Convert percent gap to days using total_days
        days = int(round((pct_gap / 100.0) * total_days))
    except Exception:
        days = 0
    return days


if __name__ == "__main__":
    # Quick sanity test
    baseline = 45.0
    actual = 42.5
    total_days = 350
    spi = calculate_spi(baseline, actual)
    days = days_ahead_behind(baseline, actual, total_days)
    print(f"Baseline %: {baseline}, Actual %: {actual}")
    print(f"SPI: {spi}")
    print(f"Days ahead(+)/behind(-): {days}")
