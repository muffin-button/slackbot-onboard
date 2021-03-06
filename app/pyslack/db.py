# Public packages
import logging
import sqlite3

# Local modules
# None


def getDb(filepath='pyslack.db'):
    """
    Returns a database connection object
    """
    return sqlite3.connect(filepath)


_db = getDb()
_db.execute('''CREATE TABLE IF NOT EXISTS protected_channels (id TEXT NOT NULL UNIQUE PRIMARY KEY, name TEXT NOT NULL)''')


def getProtectedChannel(id: str):
    """
    Retrieves details for a protected channel from the database
    """
    db = getDb()
    logging.info(f'{__name__}.getProtectedChannel :: Getting record with id [{id}]')

    exists = db.execute('''SELECT id, name FROM protected_channels WHERE id = :id''', {'id': id}).fetchone()
    return exists


def addProtectedChannel(id: str, name: str):
    """
    Adds a protected channel to the database
    """
    db = getDb()
    logging.info(f'{__name__}.addProtectedChannel :: Adding record [({id}, {name})]')

    exists = getProtectedChannel(id)
    logging.info(f'{__name__}.addProtectedChannel :: Record exists? [{exists}]')

    cur = db.cursor()

    if (exists is None):
        logging.info(f'{__name__}.addProtectedChannel :: Record does not exist')
        cur.execute('''INSERT INTO protected_channels (id, name) VALUES (?, ?)''', (id, name))
        db.commit()

    return getProtectedChannel(id)


def deleteProtectedChannel(id: str):
    """
    Deletes a protected channel from the database
    """
    db = getDb()
    logging.info(f'{__name__}.deleteProtectedChannel :: Deleting record with id [{id}]')

    db.execute('''DELETE FROM protected_channels WHERE id = :id''', {'id': id})
    db.commit()
    return


def getProtectedChannels():
    """
    Retrieves a list of all protected channels from the database
    """
    db = getDb()
    logging.info(f'{__name__}.getProtectedChannels :: Getting all records')

    query = db.execute('SELECT id, name FROM protected_channels')
    results = []
    for row in query.fetchall():
        results.append({
            'id': row[0],
            'name': row[1],
        })
    return results
