import sqlite3
from config.config import VIDEO_TYPE, DB_PATH


class Database(object):

    def __init__(self, DB, DB_TYPE):
        self.db_type = DB_TYPE
        self.con = sqlite3.connect(DB, check_same_thread=False)
        # self.init_db()

    def close(self):
        self.con.close()

    def init_db(self):
        cur = self.con.cursor()
        video_info = '''CREATE TABLE IF NOT EXISTS %s
                (
                  id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                  videoTitle    VARCHAR(20),
                  videoHtmlUrl  VARCHAR(20),
                  videoUrl    VARCHAR(20),
                  videoDuration VARCHAR(20),
                  videoPic   VARCHAR(20),
                  author    VARCHAR(20),
                  viewNum  INTEGER,
                  uploadTime DATETIME,
                  date TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime'))
                );
        ''' % self.db_type
        cur.execute(video_info)
        self.con.commit()

    def run_query(self, cmd, param=None):
        cur = self.con.cursor()
        if param is None:
            cur.executemany(cmd)
        else:
            cur.executemany(cmd, param)
        self.con.commit()

    def insert_video_info(self, param):
        sql_cmd = "INSERT INTO DefaultVideoInfo (videoTitle, videoHtmlUrl, videoUrl, videoDuration, videoPic, author, viewNum, uploadTime) VALUES (?,?,?,?,?,?,?,?)"
        self.run_query(sql_cmd, param)


if __name__ == '__main__':
    for db_type in VIDEO_TYPE.get('DB').values():
        print(db_type)
        db = Database(DB_PATH, db_type)
        db.init_db()
