import sqlite3
import traceback

from structlog import get_logger


connection = sqlite3.connect('db/db.sqlite3', check_same_thread=False)


def reset_thread(thread_id: str):
    cursor = connection.cursor()
    # try to delete the thread_id from the checkpoints and writes tables
    try:
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM checkpoint_writes WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM checkpoint_blobs WHERE thread_id = ?", (thread_id,))
        connection.commit()
        return True
    except Exception as exception:
        get_logger('db').error('error_during_thread_reset', exc_info=True, exc=traceback.format_exc())
