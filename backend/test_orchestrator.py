"""Quick test script for the Master Orchestrator"""
import asyncio
import sys
from orchestrator.master_orchestrator import run_full_analysis

# Sample project data for testing
TEST_PROJECT_DATA = {
    'project': {
        'id': 'PRJ-2025-TEST',
        'name': 'Test Construction Project',
        'type': 'Commercial',
        'location': {
            'lat': 37.7749,  # San Francisco
            'lon': -122.4194
        },
        'contract_value': 15000000,
        'start_date': '2025-01-15',
        'planned_completion': '2025-12-31'
    },
    'schedule': {
        'baseline_pct_complete': 45.0,
        'actual_pct_complete': 42.5,
        'total_days': 350,
        'days_elapsed': 148,
        'days_remaining': 202
    },
    'budget': {
        'total': 15000000,
        'spent_to_date': 6800000,
        'committed': 2250000,
        'contingency': 750000
    },
    'latest_metrics': {
        'spi': 0.944,
        'cpi': 0.936,
        'cost_variance': -426000,
        'schedule_variance_days': -9
    }
}

async def test_orchestrator():
    """Test the full orchestrator"""
    print("\n" + "="*70)
    print(" TESTING CONSTRUCTION AI - 14 AGENT ORCHESTRATOR")
    print("="*70 + "\n")
    
    print("Test Configuration:")
    print(f"  Project: {TEST_PROJECT_DATA['project']['name']}")
    print(f"  Contract Value: ${TEST_PROJECT_DATA['budget']['total']:,}")
    print(f"  Completion: {TEST_PROJECT_DATA['schedule']['actual_pct_complete']}%")
    print(f"  SPI: {TEST_PROJECT_DATA['latest_metrics']['spi']}")
    print(f"  CPI: {TEST_PROJECT_DATA['latest_metrics']['cpi']}")
    print()
    
    try:
        # Run the analysis
        results = await run_full_analysis(TEST_PROJECT_DATA)
        
        print("\n" + "="*70)
        print(" ANALYSIS COMPLETE - RESULTS SUMMARY")
        print("="*70 + "\n")
        
        print(f"✅ Session ID: {results['session_id']}")
        print(f"✅ Total Duration: {results['total_duration_seconds']:.2f} seconds")
        print(f"✅ Agents Executed: {len(results['agents'])}/14")
        print()
        
        # Check each agent
        print("Agent Execution Status:")
        agent_names = [
            'agent_1_schedule', 'agent_2_cost', 'agent_3_subcontractor',
            'agent_4_weather', 'agent_5_supply_chain', 'agent_6_change_orders',
            'agent_7_productivity', 'agent_8_quality', 'agent_9_progress',
            'agent_10_cash_flow', 'agent_11_delay_cause', 'agent_12_completion',
            'agent_13_cost_forecast', 'agent_14_risk_mitigation'
        ]
        
        errors = []
        for i, agent_name in enumerate(agent_names, 1):
            if agent_name in results['agents']:
                agent_data = results['agents'][agent_name]
                if 'error' in agent_data:
                    print(f"  ❌ Agent {i:2d}: {agent_name:25s} - ERROR: {agent_data['error']}")
                    errors.append((i, agent_name, agent_data['error']))
                else:
                    risk_score = agent_data.get('risk_score', 'N/A')
                    print(f"  ✅ Agent {i:2d}: {agent_name:25s} - Risk: {risk_score}")
            else:
                print(f"  ⚠️  Agent {i:2d}: {agent_name:25s} - NOT FOUND")
                errors.append((i, agent_name, "Agent not executed"))
        
        print()
        
        # Show overall health
        mitigation = results['agents'].get('agent_14_risk_mitigation', {})
        if mitigation and not mitigation.get('error'):
            print("="*70)
            print(" OVERALL PROJECT ASSESSMENT")
            print("="*70)
            print(f"\n🏥 Overall Health: {mitigation.get('overall_health', 'UNKNOWN')}")
            print(f"🤖 Ollama Used: {'Yes' if mitigation.get('ollama_used') else 'No (Fallback)'}")
            
            top_risks = mitigation.get('top_risks', [])
            if top_risks:
                print(f"\n🚨 Top {len(top_risks)} Risk Factors:")
                for risk in top_risks:
                    print(f"   - {risk.get('factor', 'Unknown')}: {risk.get('score', 0)}/100")
            
            recommendations = mitigation.get('recommendations', [])
            if recommendations:
                print(f"\n💡 Generated {len(recommendations)} Recommendations")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"\n   {i}. [{rec.get('priority', 'UNKNOWN')}] {rec.get('action', 'N/A')}")
                    print(f"      Impact: {rec.get('expected_impact', 'N/A')}")
            
            exec_summary = mitigation.get('executive_summary', '')
            if exec_summary:
                print("\n" + "="*70)
                print(exec_summary)
                print("="*70)
        
        print()
        
        # Error summary
        if errors:
            print("\n" + "="*70)
            print(" ⚠️  ERRORS ENCOUNTERED")
            print("="*70)
            for agent_num, agent_name, error_msg in errors:
                print(f"\nAgent {agent_num} ({agent_name}):")
                print(f"  {error_msg}")
            print()
            return False
        else:
            print("\n" + "="*70)
            print(" ✅ ALL AGENTS EXECUTED SUCCESSFULLY!")
            print("="*70 + "\n")
            return True
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔧 Construction AI - Orchestrator Test Suite\n")
    
    # Run the test
    success = asyncio.run(test_orchestrator())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

