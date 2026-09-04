import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        database='Helasabili',
        user='postgres',
        password='Chris6658'
    )
    print('✓ Connection successful!')
    
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM "Inventories"')
    count = cursor.fetchone()[0]
    print(f'✓ Total inventories: {count}')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
