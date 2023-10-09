import sqlite3


class Database:
    db = sqlite3.connect('gpt_bot')
    c = db.cursor()

    @classmethod
    def add_user(cls, user_id, sub_date, sub_type="basic", tokens_used=0):
        Database.c.execute("SELECT * FROM user_info WHERE user_id = ?",
                           (user_id, ))
        if len(Database.c.fetchall()) == 0:
            Database.c.execute("INSERT INTO user_info VALUES (?, ?, ?, ?)",
                               (user_id, sub_type, sub_date, tokens_used))
        else:
            print("Error: User already exists")
        Database.db.commit()

    @classmethod
    def add_tokens(cls, user_id, tokens):
        Database.c.execute("UPDATE user_info SET tokens_used = tokens_used + ? WHERE user_id = ?",
                           (tokens, user_id))
        Database.db.commit()

    @classmethod
    def add_message(cls, user_id, message, role):
        Database.c.execute("SELECT * FROM user_history WHERE user_id = ?",
                           (user_id, ))
        message_count = len(Database.c.fetchall())
        Database.c.execute("INSERT INTO user_history VALUES (?, ?, ?, ?)",
                           (user_id, message_count, message, role))
        if message_count > 6:
            Database.c.execute("DELETE FROM user_history WHERE user_id = ? AND message_number = ?",
                               (user_id, 1))
            Database.db.commit()
            for i in range(2, 11):
                Database.c.execute("UPDATE user_history SET message_number = ? - 1 WHERE user_id = ? AND message_number = ?",
                                   (i, user_id, i))
        Database.db.commit()

    @classmethod
    def get_history(cls, user_id):
        Database.c.execute("SELECT message_text, message_role FROM user_history WHERE user_id = ?",
                           (user_id, ))
        history = []
        for message in Database.c.fetchall():
            history.append({"role": message[1], "content": message[0]})
        return history
