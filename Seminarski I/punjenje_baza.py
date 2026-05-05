import mysql.connector
import psycopg2
import json
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
NUM_USERS = 5000

# Konfiguracije konekcija
pg_config = {
    "host": "localhost", "port": 5432, "user": "root", "password": "root", "database": "db"
}
mysql_config = {
    "host": "localhost", "port": 3306, "user": "root", "password": "root", "database": "db"
}

def generate_data():
    print(f"Generišem podatke za {NUM_USERS} korisnika...")
    users = []
    for i in range(1, NUM_USERS + 1):
        username = f"{fake.user_name()}_{i}"
        prefs = {"theme": random.choice(["dark", "light"]), "notifications": random.choice([True, False])}
        
        # Generisanje transakcija za ovog korisnika
        user_transactions = []
        for _ in range(random.randint(0, 10)):
            user_transactions.append({
                "amount": round(random.uniform(5.0, 5000.0), 2),
                "status": random.choice(['pending', 'completed', 'failed']),
                "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
            })
            
        # Generisanje logova za ovog korisnika
        user_logs = []
        for _ in range(random.randint(0, 10)):
            user_logs.append({
                "action": random.choice(['login', 'logout', 'update', 'view', 'error']),
                "meta": f"IP: 192.168.1.{random.randint(1, 254)}",
                "date": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d %H:%M:%S')
            })
            
        users.append({
            "username": username,
            "prefs": json.dumps(prefs),
            "transactions": user_transactions,
            "logs": user_logs
        })
    return users

def seed_postgres(data):
    conn = psycopg2.connect(**pg_config)
    cur = conn.cursor()
    print("Unosim podatke u PostgreSQL...")
    try:
        for u in data:
            cur.execute("INSERT INTO users (username, preferences) VALUES (%s, %s) RETURNING id", (u['username'], u['prefs']))
            u_id = cur.fetchone()[0]
            
            for t in u['transactions']:
                cur.execute("INSERT INTO transactions (user_id, amount, status, created_at) VALUES (%s, %s, %s, %s)",
                            (u_id, t['amount'], t['status'], t['date']))
            for l in u['logs']:
                cur.execute("INSERT INTO activity_logs (user_id, action_type, metadata, occurred_at) VALUES (%s, %s, %s, %s)",
                            (u_id, l['action'], l['meta'], l['date']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PG Greška: {e}")
    finally:
        cur.close()
        conn.close()

def seed_mysql(data):
    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    print("Unosim podatke u MySQL...")
    try:
        for u in data:
            cur.execute("INSERT INTO users (username, preferences) VALUES (%s, %s)", (u['username'], u['prefs']))
            u_id = cur.lastrowid
            
            for t in u['transactions']:
                cur.execute("INSERT INTO transactions (user_id, amount, status, created_at) VALUES (%s, %s, %s, %s)",
                            (u_id, t['amount'], t['status'], t['date']))
            for l in u['logs']:
                cur.execute("INSERT INTO activity_logs (user_id, action_type, metadata, occurred_at) VALUES (%s, %s, %s, %s)",
                            (u_id, l['action'], l['meta'], l['date']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"MySQL Greška: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    all_data = generate_data()
    seed_postgres(all_data)
    seed_mysql(all_data)
    print("Gotovo! Obe baze su identično popunjene.")