import sqlite3
import os


def main():
    print("A database file " + file_name + " was created.\n")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
        name TEXT PRIMARY KEY,
        password TEXT,
        balance FLOAT,
        email TEXT,
        total FLOAT)
        """)
    print("A table of the users was created.\n")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins(
        name TEXT PRIMARY KEY,
        password TEXT)
        """)
    print("A table of the admins was created.\n")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products(
        barcode TEXT PRIMARY KEY,
        name TEXT,
        price FLOAT)
        """)
    print("A table of the products was created.\n")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history(
        time TIMESTAMP,
        name TEXT,
        action TEXT,
        barcode TEXT,
        product_name TEXT,
        amount FLOAT)
        """)
    print("A table of the users' history was created.\n")

    cur.execute("INSERT INTO admins VALUES ('{}', '{}')".format("admin", "password"))
    print("An admin with the name 'admin' and the password 'password' was created.")

    con.commit()

    lines = ["title = Barcode Reader 2",
             "first timeout = 12000",
             "second timeout = 4000",
             "splash time = 500",
             "background color = black",
             "foreground color = white",
             "font = Helvetica",
             "font size = 24",
             "accent font size = 14",
             "padding = 30",
             "history displayed when buy = 5"
             "history displayed website = 50"]
    with open('settings.txt', 'w') as f:
        for line in lines:
            f.write(line)
            f.write('\n')
    print("Settings document created with default values.\n")

    os.mkdir("./backups")
    print("Backup directory created.\n")

    print("Installation done.\n")


if __name__ == '__main__':
    file_name = "items.db"

    con = sqlite3.connect(file_name)
    cur = con.cursor()
    main()
