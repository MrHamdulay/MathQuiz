import psycopg2

from flask import g

from mathquiz import app, config, SCHEMA_VERSION

@app.before_request
def create_database():
    g.database = psycopg2.connect('user=%s' % config.database_user)

    # ensure schema versions are equal
    c = g.database.cursor()
    c.execute("SELECT value FROM app_settings WHERE key = 'schema_version'")
    db_schema_version = c.fetchone()[0]
    print db_schema_version
    if str(SCHEMA_VERSION) != db_schema_version:
        raise Exception('Database schema version not the same as app version, UPGRADE')




@app.teardown_request
def close_database(request):
    g.database.close()
    return request
