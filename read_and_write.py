import sqlite3
import sys
import time


class Database:
    def __init__(self, table):
        file_name = "items.db"

        self.table = table
        self.is_table_allowed()  # raises an error if the table is not allowed

        self.con = sqlite3.connect(file_name)
        self.cur = self.con.cursor()

    def is_table_allowed(self):
        tables = ["users", "admins", "products", "history"]

        if self.table not in tables:
            raise ValueError("The table does not exist in the database.")

    def read(self, primary_key):
        match self.table:
            case "users":
                self.cur.execute("SELECT * FROM '{}' WHERE name = '{}'".format(self.table, primary_key))
                res = self.cur.fetchone()
                name = res[0]
                password = res[1]
                balance = res[2]
                email = res[3]
                total = res[4]

                user = {"name": name, "password": password, "balance": balance, "email": email, "total": total}
                return user

            case "admins":
                self.cur.execute("SELECT * FROM '{}' WHERE name = '{}'".format(self.table, primary_key))
                res = self.cur.fetchone()
                name = res[0]
                password = res[1]

                admin = {"name": name, "password": password}
                return admin

            case "products":
                self.cur.execute("SELECT * FROM '{}' WHERE barcode = '{}'".format(self.table, primary_key))
                res = self.cur.fetchone()
                barcode = res[0]
                name = res[1]
                price = res[2]

                product = {"barcode": barcode, "name": name, "price": price}
                return product

            case "history":
                settings = read_settings()
                number = settings["history displayed website"]
                self.cur.execute("SELECT * FROM '{}' WHERE name = '{}' ORDER BY time DESC LIMIT {}".format(self.table, primary_key, number))
                res = self.cur.fetchall()

                timestamp = [res[i][0] for i in range(len(res))]
                name = [res[i][1] for i in range(len(res))]
                action = [res[i][2] for i in range(len(res))]
                barcode = [res[i][3] for i in range(len(res))]
                product_name = [res[i][4] for i in range(len(res))]
                amount = [res[i][5] for i in range(len(res))]

                history = {"time": timestamp, "name": name, "action": action, "barcode": barcode, "product name": product_name, "amount": amount}
                return history

    # it updates the entire row every time, it would be more efficient to only update the changed column, but this is
    # easier and to call, so we do it this way.
    def save(self, dic):
        match self.table:
            case "users":
                name = dic["name"]
                password = dic["password"]
                balance = dic["balance"]
                email = dic["email"]
                total = dic["total"]

                self.cur.execute("UPDATE '{}' SET password = '{}' WHERE name = '{}'".format(self.table, password, name))
                self.cur.execute("UPDATE '{}' SET balance = '{}' WHERE name = '{}'".format(self.table, balance, name))
                self.cur.execute("UPDATE '{}' SET email = '{}' WHERE name = '{}'".format(self.table, email, name))
                self.cur.execute("UPDATE '{}' SET total = '{}' WHERE name = '{}'".format(self.table, total, name))
                self.con.commit()

            case "admins":
                name = dic["name"]
                password = dic["password"]

                self.cur.execute("UPDATE '{}' SET password = '{}' WHERE name = '{}'".format(self.table, password, name))
                self.con.commit()

            case "products":
                barcode = dic["barcode"]
                name = dic["name"]
                price = dic["price"]

                self.cur.execute("UPDATE '{}' SET name = '{}' WHERE barcode = '{}'".format(self.table, name, barcode))
                self.cur.execute("UPDATE '{}' SET price = '{}' WHERE barcode = '{}'".format(self.table, price, barcode))
                self.con.commit()

            case "history":
                # todo set a maximum length of the table and use update of the oldest entry instead of insert when it goes over the limit
                timestamp = dic["time"]
                name = dic["name"]
                action = dic["action"]
                barcode = dic["barcode"]
                product_name = dic["product name"]
                amount = dic["amount"]

                tup = "('{}', '{}', '{}', '{}', '{}', '{}')".format(timestamp, name, action, barcode, product_name, amount)
                self.cur.execute("INSERT INTO '{}' VALUES {}".format(self.table, tup))
                self.con.commit()

    def new(self, dic):
        match self.table:
            case "users":
                name = dic["name"]
                password = dic["password"]
                balance = dic["balance"]
                email = dic["email"]
                total = dic["total"]

                tup = "('{}', '{}', '{}', '{}', '{}')".format(name, password, balance, email, total)
                self.cur.execute("INSERT INTO '{}' VALUES {}".format(self.table, tup))
                self.con.commit()

            case "admins":
                name = dic["name"]
                password = dic["password"]

                tup = "('{}', '{}')".format(name, password)
                self.cur.execute("INSERT INTO '{}' VALUES {}".format(self.table, tup))
                self.con.commit()

            case "products":
                barcode = dic["barcode"]
                name = dic["name"]
                price = dic["price"]

                tup = "('{}', '{}', '{}')".format(barcode, name, price)
                self.cur.execute("INSERT INTO '{}' VALUES {}".format(self.table, tup))
                self.con.commit()

            case "history":
                raise ValueError("history cannot use this method.")

    def remove(self, primary_key):
        match self.table:
            case "users":
                self.cur.execute("DELETE FROM '{}' WHERE name = '{}'".format(self.table, primary_key))
                self.con.commit()

            case "admins":
                self.cur.execute("DELETE FROM '{}' WHERE name = '{}'".format(self.table, primary_key))
                self.con.commit()

            case "products":
                self.cur.execute("DELETE FROM '{}' WHERE barcode = '{}'".format(self.table, primary_key))
                self.con.commit()

            case "history":
                raise ValueError("history cannot use this method.")

    def exists(self, primary_key):
        res = None
        match self.table:
            case "users":
                self.cur.execute("SELECT * FROM '{}' WHERE name = '{}'".format(self.table, primary_key))
                res = self.cur.fetchone()

            case "admins":
                self.cur.execute("SELECT * FROM '{}' WHERE name = '{}'".format(self.table, primary_key))
                res = self.cur.fetchone()

            case "products":
                self.cur.execute("SELECT * FROM '{}' WHERE barcode = '{}'".format(self.table, primary_key))
                res = self.cur.fetchone()

            case "history":
                raise ValueError("history cannot use this method.")

        if res is None:
            return False
        else:
            return True

    def read_all(self):
        match self.table:
            case "users":
                self.cur.execute("SELECT * FROM '{}'".format(self.table))
                res = self.cur.fetchall()

                names = [res[i][0] for i in range(len(res))]
                passwords = [res[i][1] for i in range(len(res))]
                balances = [res[i][2] for i in range(len(res))]
                emails = [res[i][3] for i in range(len(res))]
                totals = [res[i][4] for i in range(len(res))]

                dic = {"names": names, "passwords": passwords, "balances": balances, "emails": emails, "totals": totals}
                return dic

            case "admins":
                self.cur.execute("SELECT * FROM '{}'".format(self.table))
                res = self.cur.fetchall()

                names = [res[i][0] for i in range(len(res))]
                passwords = [res[i][1] for i in range(len(res))]

                dic = {"names": names, "passwords": passwords}
                return dic

            case "products":
                self.cur.execute("SELECT * FROM '{}'".format(self.table))
                res = self.cur.fetchall()

                barcodes = [res[i][0] for i in range(len(res))]
                names = [res[i][1] for i in range(len(res))]
                prices = [res[i][2] for i in range(len(res))]

                dic = {"barcodes": barcodes, "names": names, "prices": prices}
                return dic

            case "history":
                raise ValueError("history cannot use this method.")


class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        # Every print, this function gets called twice, once where has length = 1. If the time_stamp is added every
        # time it will result in the time stamp printing twice.
        if len(message) != 1:
            time_stamp = time.ctime(time.time())
            message = time_stamp + "\t" + message + "\n"  # adding a newline between all print to make it easier to read

        self.terminal.write(message)
        self.log.write(message)

    # needed for compatibility, but does nothing
    def flush(self):
        pass


def read_settings():
    with open('settings.txt') as f:
        lines = [line.split("=") for line in f.readlines()]

    settings = {}
    for i in range(len(lines)):
        key = lines[i][0].strip()
        value = lines[i][1].strip()

        settings[key] = value

    return settings



