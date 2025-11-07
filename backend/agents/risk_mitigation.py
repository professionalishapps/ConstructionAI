"""Agent 14: Risk Mitigation Recommender

Aggregates all agent outputs and uses Ollama LLM to generate tailored recommendations.
Depends on all other agents (1-13).
"""
from typing import Dict, List, Tuple, Optional
import json


def aggregate_agent_outputs(
    all_agent_results: Dict[str, any]
) -> Dict[str, any]:
    """Aggregate and summarize outputs from all 13 agents.
    
    Args:
        all_agent_results: Dict with results from agents 1-13
    
    Returns:
        Dict with aggregated summary
    """
    summary = {
        'overall_health': 'Unknown',
        'risk_scores': {},
        'key_metrics': {},
        'top_risks': [],
        'opportunities': []
    }
    
    # Extract key metrics
    if 'agent_1_schedule' in all_agent_results:
        summary['key_metrics']['spi'] = all_agent_results['agent_1_schedule'].get('spi', 1.0)
        summary['key_metrics']['days_behind'] = all_agent_results['agent_1_schedule'].get('days_behind', 0)
    
    if 'agent_2_cost' in all_agent_results:
        summary['key_metrics']['cpi'] = all_agent_results['agent_2_cost'].get('cpi', 1.0)
        summary['key_metrics']['cost_variance'] = all_agent_results['agent_2_cost'].get('cost_variance', 0)
    
    # Collect risk scores
    risk_score_fields = {
        'agent_3_subcontractor': 'subcontractor_risk',
        'agent_4_weather': 'weather_risk',
        'agent_5_supply_chain': 'supply_chain_risk',
        'agent_6_change_orders': 'change_order_risk',
        'agent_7_productivity': 'productivity_risk',
        'agent_8_quality': 'quality_risk',
        'agent_10_cash_flow': 'liquidity_risk',
        'agent_11_delay_cause': 'delay_risk',
        'agent_12_completion': 'schedule_forecast_risk',
        'agent_13_cost_forecast': 'cost_forecast_risk'
    }
    
    for agent_key, risk_name in risk_score_fields.items():
        if agent_key in all_agent_results:
            risk_score = all_agent_results[agent_key].get('risk_score', 0)
            summary['risk_scores'][risk_name] = risk_score
            
            # Identify top risks (score > 60)
            if risk_score > 60:
                summary['top_risks'].append({
                    'category': risk_name.replace('_', ' ').title(),
                    'score': risk_score,
                    'level': 'HIGH'
                })
    
    # Calculate overall project health
    if summary['risk_scores']:
        avg_risk = sum(summary['risk_scores'].values()) / len(summary['risk_scores'])
        
        if avg_risk < 30:
            summary['overall_health'] = 'GREEN'
        elif avg_risk < 60:
            summary['overall_health'] = 'YELLOW'
        else:
            summary['overall_health'] = 'RED'
    
    # Sort top risks by score
    summary['top_risks'] = sorted(summary['top_risks'], key=lambda x: x['score'], reverse=True)[:5]
    
    return summary


def identify_top_risk_factors(
    agent_summary: Dict[str, any],
    limit: int = 3
) -> List[Dict[str, any]]:
    """Identify the top risk factors from aggregated data.
    
    Args:
        agent_summary: Aggregated agent summary
        limit: Number of top risks to return
    
    Returns:
        List of top risk factors with details
    """
    top_risks = []
    
    # Get top risks from summary
    for risk in agent_summary.get('top_risks', [])[:limit]:
        risk_detail = {
            'factor': risk['category'],
            'score': risk['score'],
            'level': risk['level'],
            'severity': 'Critical' if risk['score'] > 80 else 'High' if risk['score'] > 60 else 'Medium'
        }
        top_risks.append(risk_detail)
    
    # Add schedule/cost if they're problematic even if not in top list
    spi = agent_summary.get('key_metrics', {}).get('spi', 1.0)
    cpi = agent_summary.get('key_metrics', {}).get('cpi', 1.0)
    
    if spi < 0.85 and not any('Schedule' in r['factor'] for r in top_risks):
        top_risks.append({
            'factor': 'Schedule Performance',
            'score': int((1 - spi) * 100),
            'level': 'HIGH',
            'severity': 'High'
        })
    
    if cpi < 0.85 and not any('Cost' in r['factor'] for r in top_risks):
        top_risks.append({
            'factor': 'Cost Performance',
            'score': int((1 - cpi) * 100),
            'level': 'HIGH',
            'severity': 'High'
        })
    
    return top_risks[:limit]


def generate_ollama_prompt(
    agent_summary: Dict[str, any],
    top_risks: List[Dict[str, any]],
    project_constraints: Optional[Dict[str, any]] = None
) -> str:
    """Generate prompt for Ollama LLM to generate recommendations.
    
    Args:
        agent_summary: Aggregated agent summary
        top_risks: Top identified risks
        project_constraints: Optional project constraints
    
    Returns:
        Formatted prompt string
    """
    # Extract key metrics
    spi = agent_summary.get('key_metrics', {}).get('spi', 1.0)
    cpi = agent_summary.get('key_metrics', {}).get('cpi', 1.0)
    days_behind = agent_summary.get('key_metrics', {}).get('days_behind', 0)
    cost_variance = agent_summary.get('key_metrics', {}).get('cost_variance', 0)
    overall_health = agent_summary.get('overall_health', 'Unknown')
    
    # Format top risks
    risk_text = "\n".join([
        f"- {risk['factor']}: Score {risk['score']}/100 ({risk['severity']} severity)"
        for risk in top_risks
    ])
    
    prompt = f"""You are a construction project risk management expert. Analyze this project data and provide specific, actionable recommendations.

PROJECT STATUS:
Overall Health: {overall_health}
Schedule Performance Index (SPI): {spi:.3f} (1.0 = on schedule)
Cost Performance Index (CPI): {cpi:.3f} (1.0 = on budget)
Schedule Variance: {days_behind} days {'behind' if days_behind > 0 else 'ahead'}
Cost Variance: ${cost_variance:,.2f}

TOP RISK FACTORS:
{risk_text}

TASK: Generate 3-5 specific, prioritized interventions to reduce project risk and get the project back on track.

For each intervention, provide:
1. Action: Specific action to take (be concrete, not generic)
2. Expected Impact: Quantified impact on schedule, cost, or risk
3. Implementation Effort: Low/Medium/High
4. Priority: Critical/High/Medium/Low

Format your response as a JSON array of intervention objects with keys: action, expected_impact, implementation_effort, priority.

Example format:
[
  {{"action": "Accelerate structural steel procurement by switching to alternative supplier with 2-week faster delivery", "expected_impact": "Recover 10-12 days on critical path", "implementation_effort": "Medium", "priority": "Critical"}},
  {{"action": "Add second crew to concrete foundation work with weekend shifts", "expected_impact": "Improve SPI by 0.08-0.10, recover 5-7 days", "implementation_effort": "High", "priority": "High"}}
]

Respond ONLY with the JSON array, no additional text."""
    
    return prompt


def call_ollama_for_recommendations(
    prompt: str,
    model: str = "gemma2:2b",
    base_url: str = "http://localhost:11434"
) -> Dict[str, any]:
    """Call Ollama API to generate recommendations.
    
    Args:
        prompt: The prompt to send
        model: Ollama model to use
        base_url: Ollama API base URL
    
    Returns:
        Dict with Ollama response
    """
    import requests
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result.get('response', '')
            
            # Try to parse JSON from response
            try:
                # Find JSON array in response
                start_idx = llm_response.find('[')
                end_idx = llm_response.rfind(']') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = llm_response[start_idx:end_idx]
                    recommendations = json.loads(json_str)
                    
                    return {
                        'success': True,
                        'recommendations': recommendations,
                        'raw_response': llm_response
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No JSON array found in response',
                        'raw_response': llm_response
                    }
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Failed to parse JSON: {str(e)}',
                    'raw_response': llm_response
                }
        else:
            return {
                'success': False,
                'error': f'Ollama API error: {response.status_code}',
                'raw_response': response.text
            }
    
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Cannot connect to Ollama. Ensure Ollama is running on localhost:11434',
            'fallback_mode': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'fallback_mode': True
        }


def generate_fallback_recommendations(
    top_risks: List[Dict[str, any]],
    agent_summary: Dict[str, any]
) -> List[Dict[str, any]]:
    """Generate rule-based recommendations if Ollama is unavailable.
    
    Args:
        top_risks: Top identified risks
        agent_summary: Aggregated agent summary
    
    Returns:
        List of recommendation dicts
    """
    recommendations = []
    
    spi = agent_summary.get('key_metrics', {}).get('spi', 1.0)
    cpi = agent_summary.get('key_metrics', {}).get('cpi', 1.0)
    
    # Schedule recommendations
    if spi < 0.9:
        recommendations.append({
            'action': 'Implement schedule acceleration plan with additional resources on critical path',
            'expected_impact': f'Improve SPI from {spi:.2f} toward 1.0, potential recovery of {int((1-spi)*100)} days',
            'implementation_effort': 'High',
            'priority': 'Critical' if spi < 0.85 else 'High'
        })
    
    # Cost recommendations
    if cpi < 0.9:
        recommendations.append({
            'action': 'Implement enhanced cost controls and value engineering review',
            'expected_impact': f'Reduce cost overrun trajectory, improve CPI from {cpi:.2f}',
            'implementation_effort': 'Medium',
            'priority': 'Critical' if cpi < 0.85 else 'High'
        })
    
    # Risk-specific recommendations
    for risk in top_risks[:2]:
        if 'Weather' in risk['factor']:
            recommendations.append({
                'action': 'Enhance weather contingency planning and protection measures',
                'expected_impact': 'Reduce weather-related delays by 30-40%',
                'implementation_effort': 'Medium',
                'priority': 'High'
            })
        elif 'Supply' in risk['factor'] or 'Material' in risk['factor']:
            recommendations.append({
                'action': 'Expedite critical material procurement and establish backup suppliers',
                'expected_impact': 'Reduce supply chain delays by 50-60%',
                'implementation_effort': 'Medium',
                'priority': 'High'
            })
        elif 'Quality' in risk['factor']:
            recommendations.append({
                'action': 'Increase inspection frequency and implement enhanced quality controls',
                'expected_impact': 'Reduce defects and rework costs by 40-50%',
                'implementation_effort': 'Low',
                'priority': 'High'
            })
        elif 'Productivity' in risk['factor']:
            recommendations.append({
                'action': 'Optimize crew composition and eliminate workflow bottlenecks',
                'expected_impact': 'Improve productivity index by 10-15%',
                'implementation_effort': 'Medium',
                'priority': 'High'
            })
    
    return recommendations[:5]


def format_recommendations_for_display(
    recommendations: List[Dict[str, any]],
    include_metadata: bool = True
) -> Dict[str, any]:
    """Format recommendations for dashboard display.
    
    Args:
        recommendations: List of recommendation dicts
        include_metadata: Whether to include metadata
    
    Returns:
        Dict with formatted recommendations
    """
    formatted = {
        'count': len(recommendations),
        'recommendations': []
    }
    
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    sorted_recs = sorted(recommendations, key=lambda x: priority_order.get(x.get('priority', 'Low'), 4))
    
    for i, rec in enumerate(sorted_recs, 1):
        formatted_rec = {
            'id': i,
            'action': rec.get('action', ''),
            'expected_impact': rec.get('expected_impact', ''),
            'implementation_effort': rec.get('implementation_effort', 'Unknown'),
            'priority': rec.get('priority', 'Medium')
        }
        
        if include_metadata:
            # Add visual indicators
            priority = rec.get('priority', 'Medium')
            if priority == 'Critical':
                formatted_rec['icon'] = '🚨'
                formatted_rec['color'] = 'red'
            elif priority == 'High':
                formatted_rec['icon'] = '⚠️'
                formatted_rec['color'] = 'orange'
            else:
                formatted_rec['icon'] = 'ℹ️'
                formatted_rec['color'] = 'blue'
        
        formatted['recommendations'].append(formatted_rec)
    
    return formatted


def generate_executive_summary(
    agent_summary: Dict[str, any],
    recommendations: List[Dict[str, any]]
) -> str:
    """Generate executive summary of project status and recommendations.
    
    Args:
        agent_summary: Aggregated agent summary
        recommendations: List of recommendations
    
    Returns:
        Executive summary string
    """
    overall_health = agent_summary.get('overall_health', 'Unknown')
    top_risks = agent_summary.get('top_risks', [])
    spi = agent_summary.get('key_metrics', {}).get('spi', 1.0)
    cpi = agent_summary.get('key_metrics', {}).get('cpi', 1.0)
    
    # Health assessment
    if overall_health == 'GREEN':
        health_text = "Project is performing well overall with manageable risks."
    elif overall_health == 'YELLOW':
        health_text = "Project requires attention with several moderate risks identified."
    else:
        health_text = "Project is in critical condition requiring immediate intervention."
    
    # Biggest risk
    biggest_risk = "project management" if not top_risks else top_risks[0]['category'].lower()
    
    # Recommended action
    recommended_action = "Continue current practices" if overall_health == 'GREEN' else \
                        recommendations[0].get('action', 'Review and implement risk mitigation plan') if recommendations else \
                        "Implement comprehensive risk mitigation plan"
    
    summary = f"""EXECUTIVE SUMMARY:
    
Project Health: {overall_health} - {health_text}

Key Performance: SPI {spi:.3f}, CPI {cpi:.3f}

Biggest Risk: {biggest_risk.title()}

Recommended Next Action: {recommended_action}

{len(recommendations)} specific interventions identified to improve project outcomes."""
    
    return summary


if __name__ == "__main__":
    # Quick test
    print("=== Risk Mitigation Recommender Test ===\n")
    
    # Mock agent results
    mock_results = {
        'agent_1_schedule': {'spi': 0.944, 'days_behind': 9},
        'agent_2_cost': {'cpi': 0.936, 'cost_variance': -426000},
        'agent_3_subcontractor': {'risk_score': 45},
        'agent_4_weather': {'risk_score': 52},
        'agent_5_supply_chain': {'risk_score': 38},
        'agent_6_change_orders': {'risk_score': 42},
        'agent_7_productivity': {'risk_score': 55},
        'agent_8_quality': {'risk_score': 35},
        'agent_10_cash_flow': {'risk_score': 40},
        'agent_11_delay_cause': {'risk_score': 48},
        'agent_12_completion': {'risk_score': 52},
        'agent_13_cost_forecast': {'risk_score': 58}
    }
    
    # Aggregate
    summary = aggregate_agent_outputs(mock_results)
    print(f"Overall Health: {summary['overall_health']}")
    print(f"Top Risks: {len(summary['top_risks'])}\n")
    
    # Identify top risks
    top_risks = identify_top_risk_factors(summary, limit=3)
    print("Top 3 Risk Factors:")
    for risk in top_risks:
        print(f"  - {risk['factor']}: {risk['score']} ({risk['severity']})")
    print()
    
    # Generate recommendations (fallback mode for test)
    recommendations = generate_fallback_recommendations(top_risks, summary)
    print(f"Generated {len(recommendations)} Recommendations:\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec['priority']}] {rec['action']}")
        print(f"   Impact: {rec['expected_impact']}")
        print(f"   Effort: {rec['implementation_effort']}\n")
    
    # Executive summary
    exec_summary = generate_executive_summary(summary, recommendations)
    print(exec_summary)

