from django.db import connection,connections


def create_db(admin_db_name, admin_db_setting, db_name):
    connections.databases[admin_db_name] = admin_db_setting
    cur = connections[admin_db_name].cursor()
    cur.execute('CREATE DATABASE ' + db_name)


def get_database_list():
    dbs = []
    cur = connection.cursor()
    cur.execute('''
      SELECT datname FROM pg_database
    ''')
    for row in cur.fetchall():
        dbs.append(row[0])
    return dbs
