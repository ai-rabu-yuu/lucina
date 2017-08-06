"""
This module contains the database code for managing MemeCoin(tm). I don't have anything else to say about it.
"""

import sqlite3
import datetime


class CoinBase:
    __database = "bank.db"

    def __init__(self):
        self.__connection = sqlite3.connect(CoinBase.__database, detect_types=sqlite3.PARSE_DECLTYPES)
        self.__cursor = self.__connection.cursor()
        self.__cursor.execute("CREATE table IF NOT EXISTS CoinBase (uid INTEGER, name TEXT, balance REAL)")
        self.__cursor.execute("CREATE table IF NOT EXISTS Ledger (date TEXT, uid1 INTEGER, uid2 INTEGER, tx REAL)")
        self.__connection.commit()

    def balance(self, uid: int):
        p_uid = (uid,)
        try:
            self.__cursor.execute("SELECT balance FROM CoinBase WHERE uid=?", p_uid)
            return 1, self.__cursor.fetchone()
        except sqlite3.Error as e:
            return -1, ["Error: " + str(e)]

    def new_user(self, uid: int, name: str):
        p_new = (uid, name, 50.0,)
        try:
            self.__cursor.execute("SELECT balance FROM CoinBase WHERE uid=?", (uid,))
            if self.__cursor.fetchone() is None:
                self.__cursor.execute("INSERT INTO CoinBase VALUES (?, ?, ?)", p_new)
                self.__connection.commit()
                return 1,
            else:
                return -1, ["exists"]
        except sqlite3.Error as e:
            return -1, ["Error: " + str(e)]

    def transfer(self, uid1: int, uid2: int, amount: float):
        if amount <= 0:
            return -1, ["invalid"]
        with self.__connection:
            try:
                self.__cursor.execute("SELECT balance FROM CoinBase WHERE uid=?", (uid1,))
                rdy1 = self.__cursor.fetchone()
                self.__cursor.execute("SELECT balance FROM CoinBase WHERE uid=?", (uid2,))
                rdy2 = self.__cursor.fetchone()

                if rdy1 is not None and rdy2 is not None and rdy1[0] > amount:
                    p_tx1 = (amount, uid1,)
                    self.__cursor.execute("UPDATE CoinBase SET balance = balance - ? WHERE uid = ?", p_tx1)

                    p_tx2 = (amount, uid2,)
                    self.__cursor.execute("UPDATE CoinBase SET balance = balance + ? WHERE uid = ?", p_tx2)

                    p_time = datetime.datetime.now()
                    self.__cursor.execute("INSERT INTO Ledger VALUES (?, ?, ?, ?)", (p_time, uid1, uid2, amount,))
                    self.__cursor.execute("INSERT INTO Ledger VALUES (?, ?, ?, ?)", (p_time, uid2, uid1, -amount,))

                    return 1,
                else:
                    error = []
                    if rdy1 is None:
                        error.append("m_uid1")
                    if rdy2 is None:
                        error.append("m_uid2")
                    if rdy1 is not None and rdy1[0] < amount:
                        error.append("insufficient")
                    return -1, error
            except sqlite3.Error as e:
                self.__connection.rollback()
                return -1, ["Error: " + str(e)]

    def transaction_history(self, uid: int):
        p_uid = (uid,)
        return self.__cursor.execute("SELECT date, uid2, tx FROM Ledger WHERE uid1=?", p_uid)