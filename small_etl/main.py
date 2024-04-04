import psycopg2
from config import from_config, to_config
import schedule
import time
import datetime


def run_process():

    conn_dest = psycopg2.connect(
        database=to_config.db_name,
        user=to_config.db_user,
        password=to_config.db_password,
        host='localhost',
        port=to_config.db_port)

    conn_source = psycopg2.connect(
        database=from_config.db_name,
        user=from_config.db_user,
        password=from_config.db_password,
        host='localhost',
        port=from_config.db_port)

    cursor_dest = conn_dest.cursor()
    cursor_dest.execute("CREATE TABLE IF NOT EXISTS users_for_mails (first_name text, last_name text, email text, group_name text, created_at timestamp)")
    cursor_dest.execute("SELECT MAX(created_at) FROM users_for_mails")
    last_loaded_timestamp = cursor_dest.fetchone()[0]
    default_timestamp = datetime.datetime(2022, 3, 31, 14, 51, 33, 925823)

    if last_loaded_timestamp is not None:
        last_loaded_timestamp = last_loaded_timestamp
    else:
        last_loaded_timestamp = default_timestamp

    cursor_source = conn_source.cursor()
    cursor_source.execute(
        "SELECT u.first_name, u.last_name, u.email, g.name, u.created_at FROM users u JOIN user_groups ug ON u.uuid = ug.user_id JOIN groups g ON ug.group_id = g.uuid WHERE created_at > %s", (last_loaded_timestamp,))
    new_data = cursor_source.fetchall()
    print('extracted data', new_data)

    cursor_dest = conn_dest.cursor()
    for row in new_data:
        cursor_dest.execute(
            "INSERT INTO users_for_mails (first_name, last_name, email, group_name, created_at) VALUES (%s, %s, %s, %s, %s)", row)
    print('inserted data', new_data)

    conn_dest.commit()
    conn_source.commit()
    cursor_dest.close()
    cursor_source.close()


schedule.every(4).hours.do(run_process)

while True:
    schedule.run_pending()
    time.sleep(1)
