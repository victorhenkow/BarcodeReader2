# Code written by Victor Henkow, December 2023
# Version v1.1-beta

# Planned future improvements:
#   remove a specific purchase
#   work directly with database files instead of converting to dictionary

import read_and_write as rw
import time

# todo require a type in to the methods string, float etc.


# A custom error for authentication problems
class AuthenticationError(Exception):
    pass


class User:
    def __init__(self, name, password=None):
        # users = {"name": {"password": password, "balance": balance, "email": E-mail, "total": total_spent}}
        self.db = rw.Database("users")  # Database object of the user
        self.history_db = rw.Database("history")  # Database object of the history

        self.name = (name.lower()).strip()
        self.__doesUserExist()
        self.user = self.db.read(self.name)

        self.password = password
        self.logged_in = False
        # if a password is given the user should get logged in
        if password is not None:
            self.logged_in = self.__login()

        self.history = self.history_db.read(self.name)

    # raises an error if the user does not exist
    def __doesUserExist(self):
        user_exist = self.db.exists(self.name)

        if not user_exist:
            # user does not exist error
            raise ValueError("The user " + self.name + " does not exist.")

    # logs in the user if the password was correct otherwise raises an error
    def __login(self):
        correct_password = self.password == self.getPassword()
        if not correct_password:
            raise AuthenticationError("Incorrect password for the user " + self.name + ".")
        else:
            return True

    @staticmethod
    def getAllUsers():
        db = rw.Database("users")
        return db.read_all()

    def changePassword(self, new_password):
        if not self.logged_in:
            # user not logged in error
            raise AuthenticationError("User " + self.name + " is not logged in.")
        elif new_password == "":
            raise ValueError("A password cannot be an empty string.")
        else:
            # password changed successfully
            self.user["password"] = new_password
            self.db.save(self.user)

    # returns the old e-mail
    def changeEmail(self, new_email):
        if not self.logged_in:
            # user not logged in error
            raise AuthenticationError("User " + self.name + " is not logged in.")
        else:
            # e-mail changed successfully
            old_email = self.user["email"]
            self.user["email"] = new_email
            self.db.save(self.user)
            return old_email

    def getHistory(self):
        return self.history

    def addHistory(self, name, action, barcode, product_name, amount):
        timestamp = time.ctime(time.time())

        # time is the local time when the action happened
        # name is the name of the user that makes the change
        # actions is either purchase or edit by admin_name
        # barcode and product are the barcode and name of the product, if it is an edit they are empty
        # amount is the amount the balance has been changed with
        dic = {"time": timestamp, "name": name, "action": action, "barcode": barcode, "product name": product_name, "amount": amount}

        self.history_db.save(dic)
        self.history = self.history_db.read(self.name)  # self.history needs to get updated

    def getName(self):
        return self.name

    def getPassword(self):
        password = self.user["password"]
        return password

    def getEmail(self):
        email = self.user["email"]
        return email

    def getBalance(self):
        balance = self.user["balance"]
        return balance

    def getTotal(self):
        return self.user["total"]

    def updateBalance(self, price):
        self.user["balance"] -= price
        self.db.save(self.user)

    def buy(self, barcode):
        product = Product(barcode)
        price = product.getPrice()

        self.user["total"] += price  # no need to save since updateBalance() saves the same file
        self.updateBalance(price)

        self.addHistory(self.name, "buy", barcode, product.getName(), price)


class Product:
    def __init__(self, barcode):
        # products = {barcode: {"name": name, "price": price}}
        self.db = rw.Database("products")  # Database object of the products

        self.barcode = (str(barcode).lower()).strip()
        self.__doesProductExist()
        self.product = self.db.read(self.barcode)

    def __doesProductExist(self):
        product_exist = self.db.exists(self.barcode)

        if not product_exist:
            # product does not exist error
            raise ValueError("There is no product with the barcode " + self.barcode + ".")

    @staticmethod
    def getAllProducts():
        db = rw.Database("products")
        return db.read_all()

    def getBarcode(self):
        return self.barcode

    def getName(self):
        return self.product["name"]

    def getPrice(self):
        return self.product["price"]


class Admin:
    def __init__(self, name, password):
        # admins = {name: {"password": password}}
        self.db = rw.Database("admins")

        self.name = (name.lower()).strip()
        self.__doesAdminExist()
        self.admin = self.db.read(self.name)

        self.password = password
        self.logged_in = self.__login()

    def __doesAdminExist(self):
        admin_exist = self.db.exists(self.name)

        if not admin_exist:
            # admin does not exist error
            raise ValueError("The admin " + self.name + " does not exist.")

    # returns True if the login was successful and False if it failed
    def __login(self):
        correct_password = self.password == self.getPassword()
        if not correct_password:
            raise AuthenticationError("Incorrect password for the admin " + self.name + ".")
        else:
            return True

    @staticmethod
    def getAllAdmins():
        db = rw.Database("admins")
        return db.read_all()

    def getName(self):
        return self.name

    def getPassword(self):
        return self.admin["password"]

    def changePassword(self, password):
        if not self.logged_in:
            # admin not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            self.admin["password"] = password
            self.db.save(self.admin)

    def addAdmin(self, new_name, password):
        if not self.logged_in:
            # not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        elif new_name == "":
            # not an acceptable name error
            raise ValueError("A name cannot be an empty String.")
        else:
            admin_exist = self.db.exists(new_name)
            if not admin_exist:
                # admin added
                dic = {"name": new_name, "password": password}
                self.db.new(dic)
            else:
                # admin already exist error
                raise ValueError("An admin with the name " + new_name + " already exist.")

        # the method returns the name

    def removeAdmin(self, name):
        if not self.logged_in:
            # admin not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            admin_exist = self.db.exists(name)

            if admin_exist:
                # admin successfully removed
                self.db.remove(name)
                return name
            else:
                # the admin does not exist error
                raise KeyError("The admin " + name + " does not exist.")

    def addUser(self, name, password, email):
        if not self.logged_in:
            # admin not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            user_db = rw.Database("users")
            user_exist = user_db.exists(name)

            if name == "":
                # not an acceptable name error
                raise ValueError("A name cannot be an empty String.")
            elif name == "admin":
                # not an acceptable name error, the username admin is used to open the admin menu
                raise ValueError("The name cannot be admin.")
            elif not user_exist:
                # new user added successfully

                # A new user always have 0 balance
                new_user = {"name": name, "password": password, "balance": 0, "email": email.lower(), "total": 0}
                user_db.new(new_user)
            else:
                # user already exist
                raise ValueError("A user with the name " + name + " already exist.")

    # removes the user and returns the users info
    def removeUser(self, name):
        if not self.logged_in:
            # admin not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            user_db = rw.Database("users")
            user_exist = user_db.exists(name)

            if not user_exist:
                # the user does not exist error
                raise ValueError("The user " + name + " does not exist.")
            else:
                # remove the user
                user = user_db.read(name)
                email = user["email"]
                balance = user["balance"]
                total = user["total"]

                user_db.remove(name)

                return name, email, balance, total

    def addBalance(self, name, added_amount):
        if not self.logged_in:
            # not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            user = User(name)
            # It is a negative amount because updateBalance() normally removes a price
            user.updateBalance(-added_amount)

            user.addHistory(name, "edit by " + self.name, "-", "-", -added_amount)

    # returns the old E-mail
    def changeUserEmail(self, name, email):
        if not self.logged_in:
            # not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            user_db = rw.Database("users")
            user_exist = user_db.exists(name)

            if not user_exist:
                raise ValueError("There is no user with the name " + name)
            else:
                # user email changed successfully
                user = user_db.read(name)
                old_email = user["email"]
                user["email"] = email
                user_db.save(user)
                return old_email

    # returns an empty string
    def changeUserPassword(self, name, password):
        if not self.logged_in:
            # not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            user_db = rw.Database("users")
            user_exist = user_db.read(name)

            if not user_exist:
                raise ValueError("There is no user with the name " + name)
            else:
                # user password changed successfully
                user = user_db.read(name)
                user["password"] = password
                user_db.save(user)

    def addProduct(self, barcode, name, price):
        if not self.logged_in:
            # not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            product_db = rw.Database("products")
            product_exist = product_db.exists(barcode)

            if barcode == "000" or barcode == "":
                # not an acceptable name error
                raise ValueError("A barcode cannot be an empty String or 000")  # "000" is reserved for a cancel command
            elif price < 0:
                # price must be positive
                raise ValueError("The price cannot be negative.")
            elif not product_exist:
                # product added successfully
                product = {"barcode": barcode, "name": name, "price": price}
                product_db.new(product)
            else:
                # product already exist error
                raise ValueError("A product with the barcode " + barcode + " already exist.")

    # returns the product's info
    def removeProduct(self, barcode):
        if not self.logged_in:
            # admin not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            product_db = rw.Database("products")
            product_exist = product_db.exists(barcode)

            if not product_exist:
                raise ValueError("There is no product with the barcode " + barcode)
            else:
                # product removed successfully
                product = product_db.read(barcode)
                name = product["name"]
                price = product["price"]

                product_db.remove(barcode)

                return barcode, name, price

    # returns the old price
    def changeProductPrice(self, barcode, price):
        if not self.logged_in:
            # not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            product_db = rw.Database("products")
            product_exist = product_db.exists(barcode)

            if not product_exist:
                raise ValueError("There is no product with the barcode " + barcode)
            else:
                # price updated successfully
                product = product_db.read(barcode)
                old_price = product["price"]
                product["price"] = price
                product_db.save(product)
                return old_price

    # returns the old one name
    def changeProductName(self, barcode, name):
        if not self.logged_in:
            # not logged in error
            raise AuthenticationError("Admin " + self.name + " is not logged in.")
        else:
            product_db = rw.Database("products")
            product_exist = product_db.exists(barcode)

            if not product_exist:
                raise ValueError("There is no product with the barcode " + barcode)
            else:
                # name updated successfully
                product = product_db.read(barcode)
                old_name = product["name"]
                product["name"] = name
                product_db.save(product)
                return old_name
