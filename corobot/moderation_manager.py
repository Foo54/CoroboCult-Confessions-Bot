import sqlite3
import datetime

DB_PATH = "data/moderation.db"

class ModerationDBManager:
	def __init__(self, db_path) -> None:
		self.db_path = db_path

		with sqlite3.connect(self.db_path) as conn:
			cursor = conn.cursor()
			cursor.execute("""
				CREATE TABLE IF NOT EXISTS mod_actions (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					action_time TIMESTAMP,
					target_id INTEGER,
					moderator_id INTEGER,
					action_type CHAR(20),
					reason TEXT
				)
			""")
			conn.commit()

	def log_mod_action(self, target_id: int, moderator_id: int, mod_action_type: str, reason: str):
		with sqlite3.connect(self.db_path) as conn:
			cursor = conn.cursor()
			cursor.execute("""
				INSERT INTO mod_actions (action_time, target_id, moderator_id, action_type, reason)
					VALUES (?, ?, ?, ?, ?)
				""",
				(
					int(datetime.datetime.now().timestamp()),
					target_id,
					moderator_id,
					mod_action_type,
					reason
				)
			)
			conn.commit()
