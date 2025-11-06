"""Generate sample data using psycopg2 to insert rows into the PostgreSQL DB."""
import os
from dotenv import load_dotenv
try:
    import pg8000
    DB_DRIVER = 'pg8000'
except Exception:
    try:
        import psycopg2
        DB_DRIVER = 'psycopg2'
    except Exception:
        raise ImportError('No supported Postgres driver found (pg8000 or psycopg2)')
from datetime import date, timedelta
import random
from decimal import Decimal

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'construction_db')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin123')

SAMPLE_PROJECT = {
    'project_id': 'PRJ-2025-001',
    'name': 'Downtown Office Complex',
    'type': 'Commercial Construction',
    'location_lat': '37.7749',
    'location_lon': '-122.4194',
    'contract_value': '15000000.00',
    'start_date': '2025-01-15',
    'planned_completion': '2025-12-31',
    'current_completion_pct': '42.5'
}


def insert_sample_project(conn):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM projects WHERE project_id=%s", (SAMPLE_PROJECT['project_id'],))
    if cur.fetchone():
        print('Sample project already exists')
        cur.close()
        return
    cur.execute(
        """
        INSERT INTO projects (project_id, name, type, location_lat, location_lon, contract_value, start_date, planned_completion, current_completion_pct)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            SAMPLE_PROJECT['project_id'], SAMPLE_PROJECT['name'], SAMPLE_PROJECT['type'],
            SAMPLE_PROJECT['location_lat'], SAMPLE_PROJECT['location_lon'], SAMPLE_PROJECT['contract_value'],
            SAMPLE_PROJECT['start_date'], SAMPLE_PROJECT['planned_completion'], SAMPLE_PROJECT['current_completion_pct']
        )
    )
    conn.commit()
    cur.close()
    print('Inserted sample project')


def insert_daily_metrics(conn, project_id, days=60):
    cur = conn.cursor()
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=days - i)
        baseline_pct = 40.0 + i * 0.2
        actual_pct = baseline_pct - random.uniform(0.0, 2.0)
        spi = round((actual_pct / baseline_pct) if baseline_pct > 0 else 1.0, 3)
        cpi = round(1.0 - random.uniform(-0.05, 0.1), 3)
        cur.execute(
            """
            INSERT INTO daily_metrics (project_id, date, spi, cpi, actual_pct_complete, cost_variance, schedule_variance_days, weather_risk_score)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                project_id, d, str(spi), str(cpi), str(round(actual_pct,2)), random.randint(-5000,5000), random.randint(-5,5), random.randint(0,50)
            )
        )
    conn.commit()
    cur.close()
    print(f'Inserted {days} daily metrics for {project_id}')


if __name__ == '__main__':
    conn = None
    try:
        if DB_DRIVER == 'pg8000':
            conn = pg8000.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=int(DB_PORT), database=DB_NAME)
            insert_sample_project(conn)
            insert_daily_metrics(conn, SAMPLE_PROJECT['project_id'], days=60)
        else:
            conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
            insert_sample_project(conn)
            insert_daily_metrics(conn, SAMPLE_PROJECT['project_id'], days=60)
    except Exception as e:
        print('Error inserting data:', e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
            print('Connection closed')
