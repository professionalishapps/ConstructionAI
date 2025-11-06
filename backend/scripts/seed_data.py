"""Insert sample data for testing"""
import os
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

try:
    import pg8000
    DB_DRIVER = 'pg8000'
except Exception:
    try:
        import psycopg2
        DB_DRIVER = 'psycopg2'
    except Exception:
        raise ImportError('No supported Postgres driver found')

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'construction_db')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin123')

def main():
    conn = None
    try:
        if DB_DRIVER == 'pg8000':
            conn = pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=int(DB_PORT), database=DB_NAME)
        else:
            conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

        cur = conn.cursor()

        # Clear existing data
        print("Clearing existing data...")
        cur.execute("DELETE FROM agent_results")
        cur.execute("DELETE FROM inspections")
        cur.execute("DELETE FROM change_orders")
        cur.execute("DELETE FROM subcontractors")
        cur.execute("DELETE FROM daily_metrics")
        cur.execute("DELETE FROM projects")

        # Insert sample project
        print("Inserting sample project...")
        cur.execute("""
            INSERT INTO projects (project_id, name, type, location_lat, location_lon, contract_value, start_date, planned_completion, current_completion_pct)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, ('PRJ-2025-001', 'Downtown Office Complex', 'Commercial', 40.7589, -73.9851, 15000000, '2025-01-15', '2025-12-31', 35.5))

        # Insert daily metrics
        print("Inserting daily metrics...")
        today = date.today()
        cur.execute("""
            INSERT INTO daily_metrics (project_id, date, spi, cpi, actual_pct_complete, cost_variance, schedule_variance_days, weather_risk_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, ('PRJ-2025-001', today, 0.95, 1.02, 35.5, -50000, -5, 3))

        # Insert subcontractors
        print("Inserting subcontractors...")
        subcontractors = [
            ('PRJ-2025-001', 'ABC Electrical', 'Electrical', 85, 92.0, 88, 0),
            ('PRJ-2025-001', 'XYZ Plumbing', 'Plumbing', 78, 85.0, 82, 1),
            ('PRJ-2025-001', 'Premier HVAC', 'HVAC', 92, 95.0, 90, 0),
        ]

        for sub in subcontractors:
            cur.execute("""
                INSERT INTO subcontractors (project_id, name, trade, performance_score, on_time_pct, quality_score, safety_incidents)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, sub)

        # Insert change orders
        print("Inserting change orders...")
        cur.execute("""
            INSERT INTO change_orders (project_id, co_number, date, amount, category, reason, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, ('PRJ-2025-001', 'CO-001', today - timedelta(days=10), 25000, 'Design Change', 'Client requested additional windows', 'Approved'))

        # Insert inspections
        print("Inserting inspections...")
        cur.execute("""
            INSERT INTO inspections (project_id, date, area, inspector, defects_found, severity, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, ('PRJ-2025-001', today - timedelta(days=2), 'Floor 3 - East Wing', 'John Smith', 2, 'Minor', 'Minor cracks in drywall, scheduled for repair'))

        # Insert agent results
        print("Inserting agent results...")
        agents = [
            ('PRJ-2025-001', 'session-001', 'Schedule Variance Analyzer', 'COMPLETED', '{"status": "on_track", "variance_days": -5, "spi": 0.95}', 150),
            ('PRJ-2025-001', 'session-001', 'Cost Variance Tracker', 'COMPLETED', '{"status": "under_budget", "variance": -50000, "cpi": 1.02}', 200),
            ('PRJ-2025-001', 'session-001', 'Weather Impact Modeler', 'COMPLETED', '{"risk_score": 3, "forecast": "Low risk"}', 100),
        ]

        for agent in agents:
            cur.execute("""
                INSERT INTO agent_results (project_id, session_id, agent_name, status, output, execution_time_ms)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
            """, agent)

        if DB_DRIVER == 'pg8000':
            conn.commit()
        else:
            conn.commit()

        cur.close()
        print("\n✅ Sample data inserted successfully!")
        print("   - 1 project (PRJ-2025-001)")
        print("   - 1 daily metric")
        print("   - 3 subcontractors")
        print("   - 1 change order")
        print("   - 1 inspection")
        print("   - 3 agent results")

    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == '__main__':
    main()
