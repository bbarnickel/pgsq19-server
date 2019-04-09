import sqlite3

class Persistence:
    TABLE_NAME = 'highscore'

    def __init__(self, conn_string, create_sample_data=False):
        self.conn = sqlite3.connect(conn_string)
        if not self._table_exists():
            self._table_create()
            if create_sample_data:
                self._create_sample_scores()

    def get_all_scores(self):
        stmt = self._start() + """
        ORDER BY difficulty ASC, score DESC"""
        yield from self._yield_results(stmt)

    def get_scores_for_name(self, name):
        stmt = self._start() + """
                  WHERE name = ?
                  ORDER BY difficulty ASC, score DESC"""
        yield from self._yield_results(stmt, (name, ))

    def get_scores_for_difficulty(self, difficulty):
        stmt = self._start() + """
                  WHERE difficulty = ?
                  ORDER BY score DESC"""
        yield from self._yield_results(stmt, (difficulty, ))

    def get_scores_for_name_and_difficulty(self, name, difficulty):
        stmt = self._start() + """
                  WHERE name = ?
                    AND difficulty = ?"""
        yield from self._yield_results(stmt, (name, difficulty))

    def save(self, name, difficulty, score):
        stmt = """REPLACE INTO {0} (name, difficulty, score) VALUES(?, ? , ?)""".format(self.TABLE_NAME)
        with self.conn:
            self.conn.execute(stmt, (name, difficulty, score))

    def _start(self):
        return """SELECT name, difficulty, score FROM {0}""".format(self.TABLE_NAME)

    def _yield_results(self, stmt, args=()):
        for row in self.conn.execute(stmt, args):
            yield (row[0], row[1], row[2])


    def _table_exists(self):
        stmt = """SELECT name FROM sqlite_master
                  WHERE type='table'
                  AND name='{0}'""".format(self.TABLE_NAME)
        for row in self.conn.execute(stmt):
            if row[0] == self.TABLE_NAME:
                return True
        return False

    def _table_create(self):
        stmt = """CREATE TABLE {0} (
            name VARCHAR,
            difficulty INT,
            score INT,
            
            PRIMARY KEY(name, difficulty))""".format(self.TABLE_NAME)
        self.conn.execute(stmt)

    def _create_sample_scores(self):
        data = [
            ('bob', 1, 60),
            ('bob', 2, 40),
            ('bob', 3, 15),
            ('alice', 1, 88),
            ('alice', 2, 39),
            ('alice', 3, 25),
            ('john', 2, 70),
            ('john', 3, 10),
        ]

        for n, d, s in data:
            self.save(n, d, s)
