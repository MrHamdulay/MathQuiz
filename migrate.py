#!/usr/bin/env python
import os
import argparse
from mathquiz import database

MIGRATION_DIR = 'migrations/'
MIGRATION_TABLE_SQL = 'CREATE TABLE migrations (id SERIAL, name VARCHAR'\
                      ', performed TIMESTAMP DEFAULT NOW());'


def createMigrationsTable(db):
    c = db.cursor()
    c.execute('select exists(select * from information_schema.tables'
              ' where table_name=\'migrations\')')
    exists = c.fetchone()[0]
    if not exists:
        c.execute(MIGRATION_TABLE_SQL)
        db.commit()
        print 'Created migration table'

    c.close()


def getDbMigrations(db):
    c = db.cursor()
    c.execute('SELECT name FROM migrations')
    res = set(row[0] for row in c)
    c.close()

    return res


def getFsMigrations():
    return set(filename for filename in os.listdir(MIGRATION_DIR)
               if filename.endswith('.sql'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser('MathChallenge migrator')
    # if this argument isn't present we're only doing a dry run
    parser.add_argument('--run', help='Do the real deal and migrate',
                        action='store_const', const=True)
    args = parser.parse_args()
    dryRun = args.run

    db = database.connect_postgres()

    createMigrationsTable(db)

    dbMigrations = getDbMigrations(db)
    fsMigrations = getFsMigrations()

    incompleteMigrations = fsMigrations - dbMigrations

    c = db.cursor()
    for i, migration in enumerate(incompleteMigrations):
        print 'Running migration %d: %s' % (i, migration)
        if dryRun:
            print '(not really)'
        else:
            with open(MIGRATION_DIR+migration) as f:
                c.execute(f.read())
                c.execute('INSERT INTO migrations (name) VALUES (%s)',
                          (migration,))
                print 'Migration %d complete' % i

                db.commit()

    c.close()
    db.commit()

    print 'All migrations complete'
