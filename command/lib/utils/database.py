from django.db import connection,connections


def create_db(admin_db_name, admin_db_setting, db_name, db_user):
    connections.databases[admin_db_name] = admin_db_setting
    cur = connections[admin_db_name].cursor()
    cur.execute('CREATE DATABASE ' + db_name)
    cur.execute('REVOKE CONNECT ON DATABASE ' + db_name + ' FROM PUBLIC')
    cur.execute('GRANT CONNECT ON DATABASE ' + db_name + ' TO ' + db_user)
    cur.execute('GRANT ALL ON ALL TABLES IN SCHEMA public TO ' + db_user)
    cur.execute('GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ' + db_user)
    cur.execute('GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO ' + db_user)


def get_database_list():
    dbs = []
    cur = connection.cursor()
    cur.execute('''
      SELECT datname FROM pg_database
    ''')
    for row in cur.fetchall():
        dbs.append(row[0])
    return dbs
