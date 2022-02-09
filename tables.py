from piccolo.table import Table
from piccolo.columns import Text, BigInt, JSON
from piccolo.engine.sqlite import SQLiteEngine

DB = SQLiteEngine(path="ArrCord.sqlite")


class PendingRequest(Table, db=DB):
    Title = Text()
    series_data = JSON()
    requester = BigInt()
    requester_name = Text()
    created = Text()
