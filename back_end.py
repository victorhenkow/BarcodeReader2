# Code written by Victor Henkow, December 2023
# Version v1.1-beta

# Planned future improvements:
#   remove a specific purchase
#   work directly with database files instead of converting to dictionary

from files import *
import time


class User:
    def __init__(self, name):
        # users = {"name": {"password": password, "balance": balance, "email": E-mail, "total": total_spent}}
        self.file_name = self.getFileName()

        self.name = (name.lower()).strip()
        self.users = readToDict(self.file_name)  # Dictionary of all the users from saved file

        self.user_exist = existInDict(self.name, self.users)  # Does the user exist or not

        self.history_file = self.getHistoryFileName()
        if self.user_exist:
            self.history = readToDictList(self.history_file)

    # returns the name of the file with all the users
    @staticmethod
    def getFileName():
        return "saves/users.pkl"

    # returns a dictionary of all the users
    @staticmethod
    def getAllUsers():
        file_name = User.getFileName()
        return readToDict(file_name)

    # returns the name if the user exist and the password is correct
    def login(self, password):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")

        elif not password == self.getPassword():
            # wrong password error
            raise KeyError("The password for user " + self.name + " is wrong.")

        else:
            return self.name

    def getHistoryFileName(self):
        return self.historyFileName(self.name)

    @staticmethod
    def historyFileName(name):
        return "saves/history/" + name + "_history.pkl"

    def getHistory(self):
        return self.history

    def addHistory(self, dic, name, action, barcode, product_name, amount):
        time_stamp = time.ctime(time.time())

        # the history of the last 100 events are saved, after that the oldest events gets deleted
        if len(dic["time"]) > 100:  # can check the length of any of the lists since they are all the same length
            del dic["time"][0]
            del dic["name"][0]
            del dic["action"][0]
            del dic["barcode"][0]
            del dic["product name"][0]
            del dic["amount"][0]

        dic["time"].append(time_stamp)
        dic["name"].append(name)
        dic["action"].append(action)
        dic["barcode"].append(barcode)
        dic["product name"].append(product_name)
        dic["amount"].append(amount)

        save(dic, self.history_file)

    def getName(self):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            return self.name

    def getPassword(self):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            password = self.users[self.name]["password"]
            return password

    def getEmail(self):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            email = self.users[self.name]["email"]
            return email

    def getBalance(self):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            balance = self.users[self.name]["balance"]
            return balance

    def getTotal(self):
        return self.users[self.name]["total"]

    def updateBalance(self, price):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            # balance updated successfully
            self.users[self.name]["balance"] -= price
            save(self.users, self.file_name)

    def buy(self, barcode):
        product = Product(barcode)
        price = product.getPrice()

        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            # successful buy
            self.users[self.name]["total"] += price  # no need to save since updateBalance() saves the same file
            self.updateBalance(price)

            self.addHistory(self.history, self.name, "buy", barcode, product.getName(), price)

    def removeLastBuy(self):
        if not self.user_exist:
            # the user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            last_name = self.history["name"][-1]
            if not last_name == self.name:
                # last balance edit was not made by the user
                raise ValueError("The last edit of the user's balance was not made by the user.")
            else:
                last_amount = self.history["amount"][-1]

                self.updateBalance(-last_amount)
                self.addHistory(self.history, self.name, "revert last buy", "-",
                                "-", -last_amount)

                # remove the last purchase from the total spent
                self.users[self.name]["total"] -= last_amount
                save(self.users, self.file_name)


class Product:
    def __init__(self, barcode):
        # products = {barcode: {"name": name, "price": price}}
        self.file_name = self.getFileName()

        self.barcode = (str(barcode).lower()).strip()
        self.products = readToDict(self.file_name)

        self.product_exist = existInDict(self.barcode, self.products)

    # returns the name of the file with all the products
    @staticmethod
    def getFileName():
        return "saves/products.pkl"

    # returns a dictionary of all the products
    @staticmethod
    def getAllProducts():
        file_name = Product.getFileName()
        return readToDict(file_name)

    def getBarcode(self):
        if not self.product_exist:
            # product does not exist error
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            return self.barcode

    def getName(self):
        if not self.product_exist:
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            return self.products[self.barcode]["name"]

    def getPrice(self):
        if not self.product_exist:
            # product does not exist error
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            return self.products[self.barcode]["price"]


# A custom error for when the admin is not logged in
class AdminLoginError(Exception):
    pass


class Admin:
    def __init__(self, name, password):
        # admins = {name: {"password": password}}
        self.file_name = "saves/admins.pkl"

        self.name = (name.lower()).strip()
        self.password = password

        self.admins = readToDict(self.file_name)
        self.admin_exist = existInDict(self.name, self.admins)
        self.logged_in = self.login()

    # returns True if the login was successful and False if it failed
    def login(self):
        if not self.admin_exist:
            # We cannot raise an error here because it would break the addAdmin() function
            return False
        else:
            correct_password = self.password == self.admins[self.name]["password"]
            if not correct_password:
                return False
            else:
                return True

    # returns True if the input password equals the password for the admin
    def checkPassword(self, password):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            return password == self.admins[self.name]["password"]

    def changePassword(self, password):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            self.admins[self.name]["password"] = password
            save(self.admins, self.file_name)

    # returns a dictionary of all the admins
    def getAllAdmins(self):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            return self.admins

    def getName(self):
        if not self.admin_exist:
            # admin does not exist error
            raise KeyError("The admin " + self.name + " does not exist.")
        else:
            return self.name

    def addAdmin(self, new_name, password):
        if self.name == "":
            # not an acceptable name error
            raise ValueError("A name cannot be an empty String.")
        elif not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            admin_exist = existInDict(new_name, self.admins)
            if not admin_exist:
                # admin added
                # The password is stored in plain text which is not optimal, but in this case it is fine I would say.
                self.admins[new_name] = {"password": password}
                save(self.admins, self.file_name)
            else:
                # admin already exist error
                raise ValueError("An admin with the name " + new_name + " already exist.")

        # the method returns the name

    def removeAdmin(self, name):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            admin = self.admins.get(name)

            if admin is not None:
                # admin successfully added
                self.admins.pop(name)
                save(self.admins, self.file_name)
                return name
            else:
                # the admin does not exist error
                raise KeyError("The admin " + name + " does not exist.")

    def addUser(self, name, password, email):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            users = User.getAllUsers()
            user_exist = existInDict(name, users)

            if name == "":
                # not an acceptable name error
                raise ValueError("A name cannot be an empty String.")
            elif name == "admin":
                # not an acceptable name error, the username admin is used to open the admin menu
                raise ValueError("The name cannot be admin.")
            elif not user_exist:
                # new user added successfully
                file_name = User.getFileName()
                history_file = User.historyFileName(name)

                # A new user always have 0 balance
                users[name] = {"password": password, "balance": 0, "email": email.lower(), "total": 0}
                save(users, file_name)

                # time is the local time when the action happened
                # name is the name of the user or admin that makes the change
                # actions is either purchase or edit by admin
                # barcode and product are the barcode and name of the product, if it is an edit they are empty
                # amount is the amount the balance has been changed with
                # every time a balance change is made it is appended to each of the lists
                history = {"time": [], "name": [], "action": [], "barcode": [], "product name": [], "amount": []}
                save(history, history_file)
            else:
                # user already exist
                raise ValueError("A user with the name " + name + " already exist.")

    # removes the user and returns the users info
    def removeUser(self, name):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            users = User.getAllUsers()
            user_exist = existInDict(name, users)

            if not user_exist:
                # the user does not exist error
                raise KeyError("The user " + name + " does not exist.")
            else:
                # remove the user
                user = User(name)

                file_name = User.getFileName()
                history_file = user.getHistoryFileName()

                removed_user = users.pop(name)
                save(users, file_name)

                email = removed_user["email"]
                balance = removed_user["balance"]
                total = removed_user["total"]

                # remove the history file
                deleteFile(history_file)

                return name, email, balance, total

    def addBalance(self, name, added_amount):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            user = User(name)
            # It is a negative amount because updateBalance() normally removes a price
            user.updateBalance(-added_amount)

            history_file = user.getHistoryFileName()
            history = readToDictList(history_file)
            user.addHistory(history, self.name, "edit by admin", "-", "-",
                            -added_amount)

    # returns the old E-mail
    def changeUserEmail(self, name, email):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            users = User.getAllUsers()
            user_exist = existInDict(name, users)

            if not user_exist:
                raise KeyError("There is no user with the name " + name)
            else:
                # user email changed successfully
                users[name]["email"] = email

                user = User(name)
                old_email = user.getEmail()
                file_name = User.getFileName()
                save(users, file_name)
                return old_email

    # returns an empty string
    # we cannot return the old password for obvious reasons, but every other change method returns a string, so this
    # one does as well for consistency
    def changeUserPassword(self, name, password):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            users = User.getAllUsers()
            user_exist = existInDict(name, users)

            if not user_exist:
                raise KeyError("There is no user with the name " + name)
            else:
                # user password changed successfully
                users[name]["password"] = password

                file_name = User.getFileName()
                save(users, file_name)
                return ""

    def addProduct(self, barcode, name, price):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            products = Product.getAllProducts()
            product_exist = existInDict(barcode, products)

            if barcode == "000" or barcode == "":
                # not an acceptable name error
                raise ValueError("A barcode cannot be an empty String or 000")  # "000" is reserved for a cancel command
            elif price < 0:
                # price must be positive
                raise ValueError("The price cannot be negative.")
            elif not product_exist:
                # product added successfully
                file_name = Product.getFileName()

                products[barcode] = {"name": name, "price": price}
                save(products, file_name)
            else:
                # product already exist error
                raise ValueError("A product with the barcode " + barcode + " already exist.")

    # returns the product's info
    def removeProduct(self, barcode):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            products = Product.getAllProducts()
            product_exist = existInDict(barcode, products)

            if not product_exist:
                raise KeyError("There is no product with the barcode " + barcode)
            else:
                # product removed successfully
                file_name = Product.getFileName()

                removed_product = products.pop(barcode)
                save(products, file_name)

                name = removed_product["name"]
                price = removed_product["price"]

                return barcode, name, price

    # returns the old price
    def changeProductPrice(self, barcode, price):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            products = Product.getAllProducts()
            product_exist = existInDict(barcode, products)

            if not product_exist:
                raise KeyError("There is no product with the barcode " + barcode)
            else:
                # price updated successfully
                file_name = Product.getFileName()

                product = Product(barcode)
                old_price = product.getPrice()
                products[barcode]["price"] = price
                save(products, file_name)
                return old_price

    # returns the old one name
    def changeProductName(self, barcode, name):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            products = Product.getAllProducts()
            product_exist = existInDict(barcode, products)

            if not product_exist:
                raise KeyError("There is no product with the barcode " + barcode)
            else:
                # name updated successfully
                file_name = Product.getFileName()

                product = Product(barcode)
                old_name = product.getName()
                products[barcode]["name"] = name
                save(products, file_name)
                return old_name
