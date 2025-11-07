"""Agent 10: Cash Flow Projector

Models cash flow needs vs available funding and identifies potential shortfalls.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


def project_cash_position(
    current_cash: float,
    daily_expenditures: List[float],
    payment_schedule: List[Dict[str, any]],
    projection_days: int = 90
) -> List[Dict[str, any]]:
    """Project daily cash position for specified period.
    
    Args:
        current_cash: Current cash balance
        daily_expenditures: List of projected daily costs
        payment_schedule: List of scheduled payments with 'date' and 'amount'
        projection_days: Number of days to project
    
    Returns:
        List of daily cash position dicts
    """
    projections = []
    cash_balance = current_cash
    today = datetime.now().date()
    
    # Create payment lookup
    payments_by_date = {}
    for payment in payment_schedule:
        try:
            payment_date = datetime.fromisoformat(payment.get('date', '')).date()
            amount = payment.get('amount', 0)
            if payment_date in payments_by_date:
                payments_by_date[payment_date] += amount
            else:
                payments_by_date[payment_date] = amount
        except:
            continue
    
    # Project each day
    for day in range(projection_days):
        projection_date = today + timedelta(days=day)
        
        # Get daily expenditure (cycle through provided list)
        daily_cost = daily_expenditures[day % len(daily_expenditures)] if daily_expenditures else 0
        
        # Check for incoming payments
        incoming_payment = payments_by_date.get(projection_date, 0)
        
        # Update cash balance
        cash_balance += incoming_payment - daily_cost
        
        projections.append({
            'date': projection_date.isoformat(),
            'incoming': incoming_payment,
            'outgoing': daily_cost,
            'net_flow': incoming_payment - daily_cost,
            'balance': round(cash_balance, 2),
            'day_number': day + 1
        })
    
    return projections


def identify_cash_shortfalls(
    cash_projections: List[Dict[str, any]],
    minimum_balance: float = 0
) -> List[Dict[str, any]]:
    """Identify periods where cash balance falls below minimum.
    
    Args:
        cash_projections: List of daily cash position dicts
        minimum_balance: Minimum acceptable cash balance
    
    Returns:
        List of shortfall periods
    """
    shortfalls = []
    in_shortfall = False
    shortfall_start = None
    shortfall_min = float('inf')
    
    for projection in cash_projections:
        balance = projection.get('balance', 0)
        date = projection.get('date', '')
        
        if balance < minimum_balance:
            if not in_shortfall:
                # Start of new shortfall period
                in_shortfall = True
                shortfall_start = date
                shortfall_min = balance
            else:
                # Continuing shortfall
                shortfall_min = min(shortfall_min, balance)
        else:
            if in_shortfall:
                # End of shortfall period
                shortfalls.append({
                    'start_date': shortfall_start,
                    'end_date': date,
                    'minimum_balance': round(shortfall_min, 2),
                    'deficit': round(minimum_balance - shortfall_min, 2) if shortfall_min < minimum_balance else 0
                })
                in_shortfall = False
                shortfall_start = None
                shortfall_min = float('inf')
    
    # Handle case where shortfall extends to end of projection
    if in_shortfall and shortfall_start:
        shortfalls.append({
            'start_date': shortfall_start,
            'end_date': 'End of projection',
            'minimum_balance': round(shortfall_min, 2),
            'deficit': round(minimum_balance - shortfall_min, 2)
        })
    
    return shortfalls


def calculate_working_capital_needs(
    average_daily_cost: float,
    payment_terms_days: int = 30,
    safety_buffer_days: int = 15
) -> Dict[str, float]:
    """Calculate recommended working capital requirements.
    
    Args:
        average_daily_cost: Average daily project expenditure
        payment_terms_days: Typical payment terms (days until receipt)
        safety_buffer_days: Additional buffer days for safety
    
    Returns:
        Dict with working capital calculations
    """
    # Working capital needed to cover payment terms period
    base_requirement = average_daily_cost * payment_terms_days
    
    # Safety buffer
    safety_buffer = average_daily_cost * safety_buffer_days
    
    # Total recommended
    total_recommended = base_requirement + safety_buffer
    
    return {
        'average_daily_cost': round(average_daily_cost, 2),
        'payment_terms_days': payment_terms_days,
        'base_requirement': round(base_requirement, 2),
        'safety_buffer': round(safety_buffer, 2),
        'total_recommended': round(total_recommended, 2),
        'buffer_days': payment_terms_days + safety_buffer_days
    }


def analyze_cash_flow_patterns(
    cash_projections: List[Dict[str, any]]
) -> Dict[str, any]:
    """Analyze patterns in cash flow.
    
    Args:
        cash_projections: List of daily cash position dicts
    
    Returns:
        Dict with cash flow analysis
    """
    if not cash_projections:
        return {
            'trend': 'No data',
            'volatility': 'Unknown',
            'observations': ['Insufficient data']
        }
    
    balances = [p.get('balance', 0) for p in cash_projections]
    net_flows = [p.get('net_flow', 0) for p in cash_projections]
    
    # Trend analysis
    start_balance = balances[0]
    end_balance = balances[-1]
    net_change = end_balance - start_balance
    
    if net_change > 0:
        trend = "Improving"
    elif net_change < 0:
        trend = "Declining"
    else:
        trend = "Stable"
    
    # Volatility analysis
    avg_balance = sum(balances) / len(balances)
    variance = sum((b - avg_balance) ** 2 for b in balances) / len(balances)
    std_dev = variance ** 0.5
    cv = (std_dev / avg_balance * 100) if avg_balance != 0 else 0
    
    if cv > 30:
        volatility = "High"
    elif cv > 15:
        volatility = "Moderate"
    else:
        volatility = "Low"
    
    # Cash burn rate
    negative_days = sum(1 for nf in net_flows if nf < 0)
    burn_rate_pct = (negative_days / len(net_flows)) * 100
    
    # Minimum balance analysis
    min_balance = min(balances)
    min_balance_day = balances.index(min_balance) + 1
    
    observations = []
    observations.append(f"Cash position {trend.lower()} over projection period")
    observations.append(f"Cash flow volatility: {volatility}")
    
    if net_change < 0:
        observations.append(f"Net cash decrease: ${abs(net_change):,.2f}")
    elif net_change > 0:
        observations.append(f"Net cash increase: ${net_change:,.2f}")
    
    if burn_rate_pct > 70:
        observations.append(f"High burn rate: {burn_rate_pct:.0f}% of days with negative flow")
    
    if min_balance < 0:
        observations.append(f"Negative balance predicted on day {min_balance_day}")
    
    return {
        'trend': trend,
        'volatility': volatility,
        'net_change': round(net_change, 2),
        'min_balance': round(min_balance, 2),
        'min_balance_day': min_balance_day,
        'avg_daily_balance': round(avg_balance, 2),
        'burn_rate_pct': round(burn_rate_pct, 1),
        'observations': observations
    }


def recommend_cash_management_actions(
    shortfalls: List[Dict[str, any]],
    working_capital_gap: float,
    trend: str,
    volatility: str
) -> List[str]:
    """Recommend cash management actions.
    
    Args:
        shortfalls: List of identified cash shortfalls
        working_capital_gap: Gap between current and needed working capital
        trend: Cash flow trend
        volatility: Cash flow volatility level
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Shortfall-specific recommendations
    if shortfalls:
        recommendations.append(f"⚠️ {len(shortfalls)} cash shortfall period(s) identified")
        recommendations.extend([
            "Arrange additional financing or credit line",
            "Accelerate owner payment schedule if possible",
            "Delay non-critical expenditures",
            "Negotiate extended payment terms with suppliers"
        ])
        
        # Calculate total deficit
        total_deficit = sum(s.get('deficit', 0) for s in shortfalls)
        if total_deficit > 0:
            recommendations.append(f"Secure minimum ${total_deficit:,.2f} in additional funding")
    
    # Working capital gap
    if working_capital_gap > 0:
        recommendations.append(f"Working capital shortfall: ${working_capital_gap:,.2f}")
        recommendations.append("Increase working capital reserves to recommended level")
    
    # Trend-based recommendations
    if trend == "Declining":
        recommendations.extend([
            "Review project spending against budget",
            "Investigate causes of cash outflow",
            "Monitor cash position daily"
        ])
    
    # Volatility-based recommendations
    if volatility == "High":
        recommendations.extend([
            "Implement more frequent cash flow monitoring",
            "Smooth payment schedules where possible",
            "Build larger cash reserves to handle volatility"
        ])
    elif volatility == "Moderate":
        recommendations.append("Continue monitoring cash flow weekly")
    
    # General best practices
    if not shortfalls and working_capital_gap <= 0:
        recommendations.append("✓ Cash position is healthy")
        recommendations.extend([
            "Maintain current cash management practices",
            "Continue weekly cash flow projections",
            "Monitor for changes in project pace"
        ])
    else:
        recommendations.extend([
            "Update cash flow projections weekly",
            "Establish weekly cash position review meetings",
            "Develop contingency funding plan"
        ])
    
    return recommendations


def calculate_liquidity_risk_score(
    shortfall_count: int,
    min_balance: float,
    working_capital_ratio: float,
    volatility: str
) -> Tuple[int, str]:
    """Calculate liquidity risk score.
    
    Args:
        shortfall_count: Number of shortfall periods
        min_balance: Minimum projected balance
        working_capital_ratio: Current WC / Required WC
        volatility: Cash flow volatility level
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    risk_score = 0
    
    # Shortfall impact (0-40 points)
    if shortfall_count > 0:
        risk_score += min(40, shortfall_count * 20)
    
    # Minimum balance impact (0-30 points)
    if min_balance < 0:
        # Negative balance is high risk
        risk_score += 30
    elif min_balance < 50000:
        # Low balance
        risk_score += 20
    elif min_balance < 100000:
        risk_score += 10
    
    # Working capital adequacy (0-20 points)
    if working_capital_ratio < 0.5:
        risk_score += 20
    elif working_capital_ratio < 0.75:
        risk_score += 15
    elif working_capital_ratio < 1.0:
        risk_score += 10
    
    # Volatility impact (0-10 points)
    if volatility == "High":
        risk_score += 10
    elif volatility == "Moderate":
        risk_score += 5
    
    risk_score = min(100, risk_score)
    
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    return risk_score, risk_level


if __name__ == "__main__":
    # Quick test
    print("=== Cash Flow Projector Test ===\n")
    
    # Test data
    current_cash = 500_000
    daily_costs = [45_000, 50_000, 40_000, 55_000, 48_000]  # Varies by day
    
    payments = [
        {'date': (datetime.now() + timedelta(days=15)).date().isoformat(), 'amount': 750_000},
        {'date': (datetime.now() + timedelta(days=45)).date().isoformat(), 'amount': 800_000},
        {'date': (datetime.now() + timedelta(days=75)).date().isoformat(), 'amount': 750_000},
    ]
    
    # Project cash flow
    projections = project_cash_position(current_cash, daily_costs, payments, 90)
    
    print(f"Current Cash: ${current_cash:,.2f}")
    print(f"Projected {len(projections)} days\n")
    
    # Identify shortfalls
    shortfalls = identify_cash_shortfalls(projections, minimum_balance=100_000)
    print(f"Cash Shortfalls: {len(shortfalls)}")
    for sf in shortfalls:
        print(f"  {sf['start_date']} to {sf['end_date']}: Min ${sf['minimum_balance']:,.2f}")
    print()
    
    # Working capital needs
    avg_cost = sum(daily_costs) / len(daily_costs)
    wc_needs = calculate_working_capital_needs(avg_cost)
    print(f"Working Capital Needs:")
    print(f"  Recommended: ${wc_needs['total_recommended']:,.2f}")
    print(f"  Current Gap: ${max(0, wc_needs['total_recommended'] - current_cash):,.2f}\n")
    
    # Analyze patterns
    analysis = analyze_cash_flow_patterns(projections)
    print(f"Cash Flow Analysis:")
    print(f"  Trend: {analysis['trend']}")
    print(f"  Volatility: {analysis['volatility']}")
    print(f"  Min Balance: ${analysis['min_balance']:,.2f} on day {analysis['min_balance_day']}\n")
    
    # Risk score
    wc_ratio = current_cash / wc_needs['total_recommended']
    risk_score, risk_level = calculate_liquidity_risk_score(
        shortfall_count=len(shortfalls),
        min_balance=analysis['min_balance'],
        working_capital_ratio=wc_ratio,
        volatility=analysis['volatility']
    )
    print(f"Liquidity Risk: {risk_score} - {risk_level}")

