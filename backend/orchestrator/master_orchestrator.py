"""Master Orchestrator for All 14 Construction AI Agents

Manages execution order based on dependencies:
- Independent agents run in parallel (1-10)
- Dependent agents run sequentially (11-13)
- Final agent aggregates all results (14)
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal

# Import all agent modules
from agents import (
    schedule_variance,
    cost_variance,
    subcontractor_score,
    weather_impact,
    supply_chain,
    change_order,
    productivity,
    quality,
    progress_analyzer,
    cash_flow,
    delay_cause,
    completion_forecast,
    cost_at_completion,
    risk_mitigation
)


class AgentOrchestrator:
    """Orchestrates execution of all 14 agents with proper dependency management."""
    
    def __init__(self):
        self.agent_results = {}
        self.execution_times = {}
        self.session_id = f"sess-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    async def run_all_agents(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all 14 agents in proper sequence.
        
        Args:
            project_data: Complete project data dictionary
        
        Returns:
            Dict with all agent results
        """
        print(f"\n{'='*60}")
        print(f"AGENT ORCHESTRATION SESSION: {self.session_id}")
        print(f"{'='*60}\n")
        
        # PHASE 1: Independent Agents (Parallel Execution)
        print("PHASE 1: Running independent agents (1-10) in parallel...")
        phase1_start = datetime.now()
        
        phase1_tasks = [
            self._run_agent_1(project_data),
            self._run_agent_2(project_data),
            self._run_agent_3(project_data),
            self._run_agent_4(project_data),
            self._run_agent_5(project_data),
            self._run_agent_6(project_data),
            self._run_agent_7(project_data),
            self._run_agent_8(project_data),
            self._run_agent_9(project_data),
            self._run_agent_10(project_data),
        ]
        
        await asyncio.gather(*phase1_tasks)
        phase1_duration = (datetime.now() - phase1_start).total_seconds()
        print(f"✓ Phase 1 completed in {phase1_duration:.2f}s\n")
        
        # PHASE 2: Dependent Agents (Sequential Execution)
        print("PHASE 2: Running dependent agents (11-13) sequentially...")
        phase2_start = datetime.now()
        
        await self._run_agent_11(project_data)
        await self._run_agent_12(project_data)
        await self._run_agent_13(project_data)
        
        phase2_duration = (datetime.now() - phase2_start).total_seconds()
        print(f"✓ Phase 2 completed in {phase2_duration:.2f}s\n")
        
        # PHASE 3: Risk Mitigation Recommender (Aggregates All)
        print("PHASE 3: Running risk mitigation recommender (Agent 14)...")
        phase3_start = datetime.now()
        
        await self._run_agent_14(project_data)
        
        phase3_duration = (datetime.now() - phase3_start).total_seconds()
        print(f"✓ Phase 3 completed in {phase3_duration:.2f}s\n")
        
        # Summary
        total_duration = phase1_duration + phase2_duration + phase3_duration
        print(f"{'='*60}")
        print(f"ALL AGENTS COMPLETED")
        print(f"Total Execution Time: {total_duration:.2f}s")
        print(f"{'='*60}\n")
        
        return {
            'session_id': self.session_id,
            'agents': self.agent_results,
            'execution_times': self.execution_times,
            'total_duration_seconds': total_duration,
            'timestamp': datetime.now().isoformat()
        }
    
    # AGENT 1: Schedule Variance Analyzer
    async def _run_agent_1(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 1: Schedule Variance Analyzer")
        
        try:
            schedule_data = data.get('schedule', {})
            spi = schedule_variance.calculate_spi(
                baseline_pct_complete=schedule_data.get('baseline_pct_complete', 45.0),
                actual_pct_complete=schedule_data.get('actual_pct_complete', 42.5)
            )
            
            days_variance = schedule_variance.days_ahead_behind(
                baseline_pct_complete=schedule_data.get('baseline_pct_complete', 45.0),
                actual_pct_complete=schedule_data.get('actual_pct_complete', 42.5),
                total_days=schedule_data.get('total_days', 350)
            )
            
            self.agent_results['agent_1_schedule'] = {
                'spi': spi,
                'days_behind': abs(days_variance) if days_variance < 0 else 0,
                'days_ahead': days_variance if days_variance > 0 else 0,
                'status': 'Behind' if days_variance < 0 else 'Ahead' if days_variance > 0 else 'On Track',
                'risk_score': int(abs((1 - spi) * 100))
            }
            
            print(f"    ✓ SPI: {spi:.3f}, Variance: {days_variance} days")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_1_schedule'] = {'error': str(e)}
        
        self.execution_times['agent_1'] = (datetime.now() - start).total_seconds()
    
    # AGENT 2: Cost Variance Tracker
    async def _run_agent_2(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 2: Cost Variance Tracker")
        
        try:
            budget_data = data.get('budget', {})
            schedule_data = data.get('schedule', {})
            
            budget = budget_data.get('total', 15000000)
            spent = budget_data.get('spent_to_date', 6800000)
            pct_complete = schedule_data.get('actual_pct_complete', 42.5)
            
            # Calculate CPI
            earned_value = budget * (pct_complete / 100)
            cpi = earned_value / spent if spent > 0 else 1.0
            cost_variance = earned_value - spent
            
            eac = cost_variance.calculate_eac(budget, cpi, spent, pct_complete)
            pressure, observations = cost_variance.analyze_cost_pressure(
                spent, budget, pct_complete, cost_variance
            )
            
            self.agent_results['agent_2_cost'] = {
                'cpi': round(cpi, 3),
                'cost_variance': round(cost_variance, 2),
                'eac': eac,
                'pressure_level': pressure,
                'observations': observations,
                'risk_score': int(abs((1 - cpi) * 100))
            }
            
            print(f"    ✓ CPI: {cpi:.3f}, Variance: ${cost_variance:,.0f}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_2_cost'] = {'error': str(e)}
        
        self.execution_times['agent_2'] = (datetime.now() - start).total_seconds()
    
    # AGENT 3: Subcontractor Performance Monitor
    async def _run_agent_3(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 3: Subcontractor Performance Monitor")
        
        try:
            # Get real subcontractor data from project
            subcontractor_data = data.get('subcontractor', {})
            
            schedule_score, msg = subcontractor_score.calculate_schedule_score(
                planned_days=subcontractor_data.get('planned_days', 30),
                actual_days=subcontractor_data.get('actual_days', 34),
                critical_path=subcontractor_data.get('critical_path', True)
            )
            
            quality_score, quality_obs = subcontractor_score.calculate_quality_score(
                defects=subcontractor_data.get('defects', 2),
                rework_hours=subcontractor_data.get('rework_hours', 8.5),
                inspections_passed=subcontractor_data.get('inspections_passed', 4),
                inspections_total=subcontractor_data.get('inspections_total', 5)
            )
            
            safety_score, safety_obs = subcontractor_score.calculate_safety_score(
                incidents=subcontractor_data.get('incidents', 0),
                near_misses=subcontractor_data.get('near_misses', 1),
                safety_observations=subcontractor_data.get('safety_observations', 3)
            )
            
            scores = {
                'schedule_adherence': schedule_score,
                'quality': quality_score,
                'safety': safety_score
            }
            
            risk_level, risk_factors = subcontractor_score.assess_risk_level(scores)
            
            self.agent_results['agent_3_subcontractor'] = {
                'scores': scores,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'risk_score': int(100 - (sum(scores.values()) / len(scores)))
            }
            
            print(f"    ✓ Avg Score: {sum(scores.values())/len(scores):.1f}, Risk: {risk_level}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_3_subcontractor'] = {'error': str(e)}
        
        self.execution_times['agent_3'] = (datetime.now() - start).total_seconds()
    
    # AGENT 4: Weather Impact Modeler
    async def _run_agent_4(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 4: Weather Impact Modeler (with Open-Meteo API)")
        
        try:
            location = data.get('project', {}).get('location', {})
            lat = float(location.get('lat', 37.7749))
            lon = float(location.get('lon', -122.4194))
            
            # Fetch real weather data
            forecast = weather_impact.fetch_weather_forecast(lat, lon, 14)
            analysis = weather_impact.analyze_weather_forecast(
                forecast, 'foundation', 14
            )
            
            self.agent_results['agent_4_weather'] = {
                'estimated_delay_days': analysis['estimated_delay_days'],
                'risk_score': analysis['risk_score'],
                'bad_weather_days': analysis['bad_weather_days'],
                'observations': analysis['observations'],
                'api_success': forecast.get('success', False)
            }
            
            print(f"    ✓ Delay: {analysis['estimated_delay_days']} days, Risk: {analysis['risk_score']}/100")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_4_weather'] = {'error': str(e), 'risk_score': 45}
        
        self.execution_times['agent_4'] = (datetime.now() - start).total_seconds()
    
    # AGENT 5: Supply Chain Disruption Detector
    async def _run_agent_5(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 5: Supply Chain Disruption Detector")
        
        try:
            # Get real materials and supplier data from project
            supply_chain_data = data.get('supply_chain', {})
            materials = supply_chain_data.get('materials', [
                {'name': 'Rebar Steel', 'lead_time_days': 21, 'stock_level': 15, 'critical': True},
                {'name': 'Concrete', 'lead_time_days': 3, 'stock_level': 80, 'critical': True},
            ])
            
            at_risk, risk_score = supply_chain.detect_material_shortages(materials)
            
            supplier_data = supply_chain_data.get('supplier_performance', {})
            score, assessment = supply_chain.calculate_supplier_reliability(
                on_time_deliveries=supplier_data.get('on_time_deliveries', 18),
                total_deliveries=supplier_data.get('total_deliveries', 20),
                lead_time_extensions=supplier_data.get('lead_time_extensions', 2)
            )
            
            self.agent_results['agent_5_supply_chain'] = {
                'at_risk_materials': at_risk,
                'risk_score': risk_score,
                'supplier_reliability': score
            }
            
            print(f"    ✓ At-risk materials: {len(at_risk)}, Risk: {risk_score}/100")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_5_supply_chain'] = {'error': str(e)}
        
        self.execution_times['agent_5'] = (datetime.now() - start).total_seconds()
    
    # AGENT 6: Change Order Pattern Analyzer
    async def _run_agent_6(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 6: Change Order Pattern Analyzer")
        
        try:
            budget = data.get('budget', {}).get('total', 15000000)
            
            # Get real change orders from project
            change_orders = data.get('change_orders', [
                {'category': 'Design Change', 'amount': 50000, 'initiated_by': 'Owner', 'date': '2025-02-15'},
                {'category': 'Owner Request', 'amount': 75000, 'initiated_by': 'Owner', 'date': '2025-05-20'},
            ])
            
            total_co_value = sum(co['amount'] for co in change_orders)
            co_rate, assessment = change_order.calculate_change_order_rate(total_co_value, budget)
            
            categorization = change_order.categorize_change_orders(change_orders)
            scope_creep, indicators = change_order.detect_scope_creep_patterns(change_orders, budget)
            
            risk_score, risk_level = change_order.calculate_change_order_risk_score(
                co_rate, scope_creep, len(change_orders), 0.2
            )
            
            self.agent_results['agent_6_change_orders'] = {
                'total_count': len(change_orders),
                'total_value': total_co_value,
                'co_rate': co_rate,
                'scope_creep_detected': scope_creep,
                'risk_score': risk_score,
                'late_phase_count': 0
            }
            
            print(f"    ✓ Change Orders: {len(change_orders)}, Rate: {co_rate}%")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_6_change_orders'] = {'error': str(e)}
        
        self.execution_times['agent_6'] = (datetime.now() - start).total_seconds()
    
    # AGENT 7: Productivity Trend Tracker
    async def _run_agent_7(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 7: Productivity Trend Tracker")
        
        try:
            # Get real productivity data from project
            productivity_data = data.get('productivity', {})
            
            rate, rate_str = productivity.calculate_productivity_rate(
                units_completed=productivity_data.get('units_completed', 450),
                labor_hours=productivity_data.get('labor_hours', 180),
                unit_type=productivity_data.get('unit_type', 'sq ft')
            )
            
            index, assessment = productivity.compare_to_benchmark(
                actual_rate=rate,
                benchmark_rate=productivity_data.get('benchmark_rate', 3.0)
            )
            
            historical = productivity_data.get('historical_rates', [
                {'date': '2025-01-01', 'rate': 3.2},
                {'date': '2025-01-08', 'rate': 3.0},
                {'date': '2025-01-15', 'rate': 2.8},
            ])
            
            decline, observations = productivity.detect_productivity_decline(historical)
            risk_score, risk_level = productivity.calculate_productivity_risk_score(
                index, decline, False
            )
            
            self.agent_results['agent_7_productivity'] = {
                'productivity_index': index,
                'decline_detected': decline,
                'risk_score': risk_score
            }
            
            print(f"    ✓ Index: {index:.3f}, Risk: {risk_score}/100")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_7_productivity'] = {'error': str(e)}
        
        self.execution_times['agent_7'] = (datetime.now() - start).total_seconds()
    
    # AGENT 8: Quality Issue Detector
    async def _run_agent_8(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 8: Quality Issue Detector")
        
        try:
            # Get real quality data from project
            quality_data = data.get('quality', {})
            
            prob, level = quality.calculate_rework_probability(
                open_defects=quality_data.get('open_defects', 4),
                recent_failures=quality_data.get('recent_failures', 2),
                inspection_pass_rate=quality_data.get('inspection_pass_rate', 10),
                historical_rework_rate=quality_data.get('historical_rework_rate', 15)
            )
            
            defects = quality_data.get('defects', [
                {'severity': 'Major', 'category': 'Concrete', 'cost_estimate': 5000},
            ])
            
            analysis = quality.analyze_defect_severity(defects)
            risk_score, risk_level = quality.calculate_quality_risk_score(
                rework_probability=prob,
                open_defects=quality_data.get('open_defects', 4),
                inspection_pass_rate=quality_data.get('inspection_pass_rate', 80),
                defect_density=quality_data.get('defect_density', 0.5)
            )
            
            self.agent_results['agent_8_quality'] = {
                'rework_probability': prob,
                'defect_count': len(defects),
                'risk_score': risk_score
            }
            
            print(f"    ✓ Rework Prob: {prob}%, Risk: {risk_score}/100")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_8_quality'] = {'error': str(e)}
        
        self.execution_times['agent_8'] = (datetime.now() - start).total_seconds()
    
    # AGENT 9: Progress Analyzer
    async def _run_agent_9(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 9: Progress Analyzer")
        
        try:
            # Get real progress data from project
            progress_data = data.get('progress', {})
            schedule_data = data.get('schedule', {})
            
            reported_pct = schedule_data.get('actual_pct_complete', 75.0)
            
            visual_pct, confidence = progress_analyzer.simulate_visual_progress_assessment(
                photo_count=progress_data.get('photo_count', 8),
                activity_type=progress_data.get('activity_type', 'framing'),
                reported_pct_complete=reported_pct
            )
            
            discrepancy, variance, status = progress_analyzer.detect_progress_discrepancy(
                visual_pct, reported_pct
            )
            
            risk_score, risk_level = progress_analyzer.calculate_progress_verification_risk(
                33.3, abs(variance), 0, 65
            )
            
            self.agent_results['agent_9_progress'] = {
                'visual_assessment': visual_pct,
                'discrepancy_detected': discrepancy,
                'variance': variance,
                'risk_score': risk_score
            }
            
            print(f"    ✓ Visual: {visual_pct}%, Variance: {variance}%")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_9_progress'] = {'error': str(e)}
        
        self.execution_times['agent_9'] = (datetime.now() - start).total_seconds()
    
    # AGENT 10: Cash Flow Projector
    async def _run_agent_10(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 10: Cash Flow Projector")
        
        try:
            # Get real cash flow data from project
            cash_flow_data = data.get('cash_flow', {})
            
            current_cash = cash_flow_data.get('current_balance', 500_000)
            daily_costs = cash_flow_data.get('recent_daily_costs', [45_000, 50_000, 40_000])
            payments = cash_flow_data.get('expected_payments', [])
            projection_days = cash_flow_data.get('projection_days', 90)
            
            projections = cash_flow.project_cash_position(current_cash, daily_costs, payments, projection_days)
            shortfalls = cash_flow.identify_cash_shortfalls(projections, 100_000)
            analysis = cash_flow.analyze_cash_flow_patterns(projections)
            
            risk_score, risk_level = cash_flow.calculate_liquidity_risk_score(
                len(shortfalls), analysis['min_balance'], 0.8, analysis['volatility']
            )
            
            self.agent_results['agent_10_cash_flow'] = {
                'shortfall_count': len(shortfalls),
                'min_balance': analysis['min_balance'],
                'risk_score': risk_score
            }
            
            print(f"    ✓ Shortfalls: {len(shortfalls)}, Min Balance: ${analysis['min_balance']:,.0f}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_10_cash_flow'] = {'error': str(e)}
        
        self.execution_times['agent_10'] = (datetime.now() - start).total_seconds()
    
    # AGENT 11: Delay Cause Identifier (Depends on 1, 4, 5, 6)
    async def _run_agent_11(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 11: Delay Cause Identifier")
        
        try:
            # Integrate data from previous agents
            integrated_delays = delay_cause.integrate_agent_data_for_delay_analysis(
                self.agent_results.get('agent_1_schedule', {}),
                self.agent_results.get('agent_4_weather', {}),
                self.agent_results.get('agent_5_supply_chain', {}),
                self.agent_results.get('agent_6_change_orders', {})
            )
            
            categorization = delay_cause.categorize_delay_incidents(integrated_delays)
            
            top_cause_pct = max(d['percentage'] for d in categorization['by_cause'].values()) if categorization['by_cause'] else 0
            risk_score, risk_level = delay_cause.calculate_delay_cause_risk_score(
                categorization['total_delay_days'],
                categorization['controllable_pct'],
                top_cause_pct
            )
            
            self.agent_results['agent_11_delay_cause'] = {
                'total_delay_days': categorization['total_delay_days'],
                'controllable_pct': categorization['controllable_pct'],
                'risk_score': risk_score
            }
            
            print(f"    ✓ Total Delays: {categorization['total_delay_days']} days, Controllable: {categorization['controllable_pct']}%")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_11_delay_cause'] = {'error': str(e)}
        
        self.execution_times['agent_11'] = (datetime.now() - start).total_seconds()
    
    # AGENT 12: Completion Date Forecaster (Depends on 1, 7, 9)
    async def _run_agent_12(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 12: Completion Date Forecaster")
        
        try:
            schedule_data = data.get('schedule', {})
            spi = self.agent_results.get('agent_1_schedule', {}).get('spi', 0.944)
            prod_index = self.agent_results.get('agent_7_productivity', {}).get('productivity_index', 0.92)
            
            remaining_days, method = completion_forecast.calculate_estimate_at_completion_time(
                current_pct_complete=42.5,
                spi=spi,
                remaining_days_baseline=202,
                method="composite"
            )
            
            forecast = completion_forecast.forecast_completion_date(
                "2025-01-15", 148, remaining_days
            )
            
            comparison = completion_forecast.compare_to_baseline_completion(
                forecast['forecast_completion_date'], "2025-12-31"
            )
            
            risk_score, risk_level = completion_forecast.calculate_completion_forecast_risk(
                comparison['variance_days'], 30, spi, "Declining"
            )
            
            self.agent_results['agent_12_completion'] = {
                'forecast_date': forecast['forecast_completion_date'],
                'variance_days': comparison['variance_days'],
                'risk_score': risk_score
            }
            
            print(f"    ✓ Forecast: {forecast['forecast_completion_date']}, Variance: {comparison['variance_days']} days")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_12_completion'] = {'error': str(e)}
        
        self.execution_times['agent_12'] = (datetime.now() - start).total_seconds()
    
    # AGENT 13: Cost at Completion Estimator (Depends on 2, 6, 10)
    async def _run_agent_13(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 13: Cost at Completion Estimator")
        
        try:
            budget = data.get('budget', {}).get('total', 15000000)
            spent = data.get('budget', {}).get('spent_to_date', 6800000)
            pct_complete = 42.5
            earned_value = budget * (pct_complete / 100)
            cpi = self.agent_results.get('agent_2_cost', {}).get('cpi', 0.936)
            
            eac_methods = cost_at_completion.calculate_eac_multiple_methods(
                budget, spent, earned_value, cpi, pct_complete
            )
            
            integrated = cost_at_completion.integrate_change_order_and_cashflow_data(
                eac_methods['composite_eac'], 150_000, "Accelerating", "MEDIUM"
            )
            
            overrun = cost_at_completion.calculate_expected_overrun(
                integrated['adjusted_eac'], budget
            )
            
            risk_score, risk_level = cost_at_completion.calculate_cost_forecast_risk(
                overrun['variance_pct'], 15, cpi, 2.5
            )
            
            self.agent_results['agent_13_cost_forecast'] = {
                'forecast_final_cost': overrun['forecast_final_cost'],
                'overrun_amount': overrun['overrun_amount'],
                'variance_pct': overrun['variance_pct'],
                'risk_score': risk_score
            }
            
            print(f"    ✓ EAC: ${overrun['forecast_final_cost']:,.0f}, Overrun: ${overrun['overrun_amount']:,.0f}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_13_cost_forecast'] = {'error': str(e)}
        
        self.execution_times['agent_13'] = (datetime.now() - start).total_seconds()
    
    # AGENT 14: Risk Mitigation Recommender (Aggregates All + Ollama)
    async def _run_agent_14(self, data: Dict) -> None:
        start = datetime.now()
        print("  → Agent 14: Risk Mitigation Recommender (with Ollama)")
        
        try:
            # Aggregate all agent outputs
            summary = risk_mitigation.aggregate_agent_outputs(self.agent_results)
            top_risks = risk_mitigation.identify_top_risk_factors(summary, limit=3)
            
            # Generate Ollama prompt
            prompt = risk_mitigation.generate_ollama_prompt(summary, top_risks)
            
            # Try Ollama, fall back to rules if unavailable
            ollama_result = risk_mitigation.call_ollama_for_recommendations(prompt)
            
            if ollama_result.get('success'):
                recommendations = ollama_result['recommendations']
                print(f"    ✓ Generated {len(recommendations)} recommendations via Ollama")
            else:
                recommendations = risk_mitigation.generate_fallback_recommendations(top_risks, summary)
                print(f"    ⚠ Ollama unavailable, using rule-based recommendations ({len(recommendations)} items)")
            
            # Generate executive summary
            exec_summary = risk_mitigation.generate_executive_summary(summary, recommendations)
            
            formatted = risk_mitigation.format_recommendations_for_display(recommendations)
            
            self.agent_results['agent_14_risk_mitigation'] = {
                'overall_health': summary['overall_health'],
                'top_risks': top_risks,
                'recommendations': formatted['recommendations'],
                'executive_summary': exec_summary,
                'ollama_used': ollama_result.get('success', False)
            }
            
            print(f"    ✓ Overall Health: {summary['overall_health']}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            self.agent_results['agent_14_risk_mitigation'] = {'error': str(e)}
        
        self.execution_times['agent_14'] = (datetime.now() - start).total_seconds()


# Convenience function for easy import
async def run_full_analysis(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run complete 14-agent analysis.
    
    Args:
        project_data: Project data dictionary
    
    Returns:
        Complete analysis results
    """
    orchestrator = AgentOrchestrator()
    return await orchestrator.run_all_agents(project_data)


if __name__ == "__main__":
    # Test with sample data
    import asyncio
    
    sample_data = {
        'project': {
            'id': 'PRJ-2025-TEST',
            'name': 'Test Project',
            'location': {'lat': 37.7749, 'lon': -122.4194}
        },
        'schedule': {
            'baseline_pct_complete': 45.0,
            'actual_pct_complete': 42.5,
            'total_days': 350
        },
        'budget': {
            'total': 15000000,
            'spent_to_date': 6800000
        }
    }
    
    print("\n" + "="*60)
    print("TESTING MASTER ORCHESTRATOR")
    print("="*60)
    
    results = asyncio.run(run_full_analysis(sample_data))
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Session ID: {results['session_id']}")
    print(f"Agents Executed: {len(results['agents'])}")
    print(f"Total Duration: {results['total_duration_seconds']:.2f}s")
    
    # Show overall health
    mitigation = results['agents'].get('agent_14_risk_mitigation', {})
    if 'overall_health' in mitigation:
        print(f"\nOverall Project Health: {mitigation['overall_health']}")
        print(f"Top Risks: {len(mitigation.get('top_risks', []))}")
        print(f"Recommendations: {len(mitigation.get('recommendations', []))}")

