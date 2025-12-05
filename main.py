import pandas as pd
from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents

DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.

    Args:
        conn: Database connection
        csv_path: Path to CSV file
        table_name: Name of the target table

    Returns:
        int: Number of rows loaded
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return 0

    df = pd.read_csv(csv_path)
    row_count = len(df)

    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)

    print(f"Loaded {row_count} rows from {csv_path.name} into {table_name}")
    return row_count


def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)

    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("       Connected")

    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)

    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    print(f"       Migrated {user_count} users")

    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    total_rows = load_all_csv_data(conn)

    # Step 5: Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()

    # Count rows in each table
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")

    conn.close()

    print("\n" + "="*60)
    print(" DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"\n Database location: {DB_PATH.resolve()}")
    print("\nYou're ready for Week 9 (Streamlit web interface)!")


# Run the complete setup
setup_database_complete()

def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)

    # # 1. Setup database
    # conn = connect_database()
    # create_all_tables(conn)

    # # 2. Migrate users
    # migrate_users_from_file(conn)

    # # 3. Test authentication
    # success, msg = register_user("alice", "SecurePass123!", "analyst")
    # print(msg)

    # success, msg = login_user("alice", "SecurePass123!")
    # print(msg)

    # # 4. Test CRUD
    # incident_id = insert_incident(
    #     "2024-11-05",
    #     "Phishing",
    #     "High",
    #     "Open",
    #     "Suspicious email detected",
    #     "alice"
    # )
    # print(f"Created incident #{incident_id}")

    # # 5. Query data
    # df = get_all_incidents()
    # print(f"Total incidents: {len(df)}")

    # conn.close()

    # # Verify users were migrated
    # conn = connect_database()
    # cursor = conn.cursor()

    # # Query all users
    # cursor.execute("SELECT id, username, role FROM users")
    # users = cursor.fetchall()

    # print(" Users in database:")
    # print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
    # print("-" * 35)
    # for user in users:
    #     print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

    # print(f"\nTotal users: {len(users)}")
    # conn.close()


if __name__ == "__main__":
    main()
