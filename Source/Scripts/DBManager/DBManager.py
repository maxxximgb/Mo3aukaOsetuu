import sqlite3
from typing import Optional, List
from Shared.LM import Level, Memorial
import json

game_state, levels = [None] * 2


class DBManager:
    def __init__(self, db_name: str = "game.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        global game_state, levels
        from Globals.Variables import game_state, levels

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS GameState (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                current_level_id INTEGER,
                puzzletime TEXT,
                CarTrips INTEGER,
                CarFaults INTEGER,
                FOREIGN KEY (current_level_id) REFERENCES Level(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Level (
                id INTEGER PRIMARY KEY,
                completed BOOLEAN NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Memorial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_id INTEGER NOT NULL,
                completed BOOLEAN NOT NULL,
                FOREIGN KEY (level_id) REFERENCES Level(id)
            )
        ''')
        self.conn.commit()

    def save_all(self):
        self.cursor.execute('''
            INSERT INTO GameState (score, current_level_id, puzzletime, CarTrips, CarFaults)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            game_state.score,
            game_state.currentlvl.id if game_state.currentlvl else None,
            json.dumps(game_state.puzzletime),
            game_state.car_trips,
            game_state.car_faults
        ))

        for level in levels:
            self.cursor.execute('''
                INSERT OR REPLACE INTO Level (id, completed)
                VALUES (?, ?)
            ''', (level.id, level.completed))

            for memorial in level.memorials:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO Memorial (id, level_id, completed)
                    VALUES (?, ?, ?)
                ''', (memorial.id, level.id, memorial.completed))

        self.conn.commit()

    def load_all(self):
        self.cursor.execute('SELECT score, current_level_id, puzzletime, CarTrips, CarFaults FROM GameState ORDER BY id DESC LIMIT 1')
        game_state_data = self.cursor.fetchone()
        if game_state_data:
            game_state.score = game_state_data[0]
            current_level_id = game_state_data[1]
            game_state.puzzletime = json.loads(game_state_data[2]) if game_state_data[2] else []
            game_state.car_trips = game_state_data[3]
            game_state.car_faults = game_state_data[4]
            if current_level_id:
                for level in levels:
                    if level.id == current_level_id:
                        game_state.currentlvl = level
                        break

        for level in levels:
            self.cursor.execute('SELECT completed FROM Level WHERE id = ?', (level.id,))
            level_data = self.cursor.fetchone()
            if level_data:
                level.completed = bool(level_data[0])
                self.cursor.execute('SELECT id, completed FROM Memorial WHERE level_id = ?', (level.id,))
                memorials_data = self.cursor.fetchall()

                for memorial_data in memorials_data:
                    for game_mem in level.memorials:
                        if game_mem.id == memorial_data[0]:
                            game_mem.completed = bool(memorial_data[1])
                            break

    def close(self):
        self.conn.close()