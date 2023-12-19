from flask import Flask, render_template, request, redirect, session, url_for
from back_end import *

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # the login privileges, can either be "user" or "admin"
        privileges = request.form["privileges"]

        if privileges == "admin":
            admin = Admin(username, password)

            try:
                admin_name = admin.getName()
            except KeyError as error:
                print("An error occurred: " + str(error))
                return redirect(url_for("login"))
            else:
                if not admin.logged_in:
                    print("Wrong password for the admin with the name " + admin_name)
                    return redirect(url_for("login"))
                else:
                    session["password"] = password
                    print("Admin " + admin_name + " has logged in.")
                    return redirect(url_for("admin_start", admin_name=admin_name))

        elif privileges == "user":
            user = User(username)

            try:
                user_name = user.login(password)
            except KeyError as error:
                print("An error occurred: " + str(error))
                return redirect(url_for("login"))
            else:
                print("The user " + user_name + " has logged in.")
                return redirect(url_for("user_start", user_name=user_name))

    else:
        return render_template("login.html")


@app.route("/user_start/<user_name>",  methods=["POST", "GET"])
def user_start(user_name):
    user = User(user_name)
    balance = user.getBalance()
    total_spent = user.getTotal()

    history = user.getHistory()
    # extract all the lists from the dictionary history
    timestamp = history["time"]
    name = history["name"]
    action = history["action"]
    barcode = history["barcode"]
    product_name = history["product name"]
    amount = history["amount"]

    products = Product.getAllProducts()
    # extract all the lists from the dictionary products
    product_barcodes = [p_barcode for p_barcode in products]
    product_names = [products[product_barcode]["name"] for product_barcode in product_barcodes]
    product_prices = [products[product_barcode]["price"] for product_barcode in product_barcodes]

    return render_template("user_start.html", user_name=user_name, balance=balance,
                           total_spent=total_spent, timestamp=timestamp, name=name, action=action, barcode=barcode,
                           product_name=product_name, amount=amount, product_barcodes=product_barcodes,
                           product_names=product_names, product_prices=product_prices)


@app.route("/admin_start/<admin_name>", methods=["POST", "GET"])
def admin_start(admin_name):
    password = session.get("password", None)
    admin = Admin(admin_name, password)

    users = admin.getAllUsers()

    # extract the lists from the dictionary users
    user_names = [name for name in users]
    user_emails = [users[user_name]["email"] for user_name in user_names]
    user_balances = [users[user_name]["balance"] for user_name in user_names]
    user_totals = [users[user_name]["total"] for user_name in user_names]

    products = Product.getAllProducts()
    # extract all the lists from the dictionary products
    product_barcodes = [p_barcode for p_barcode in products]
    product_names = [products[product_barcode]["name"] for product_barcode in product_barcodes]
    product_prices = [products[product_barcode]["price"] for product_barcode in product_barcodes]

    admins = admin.getAllAdmins()
    # create a list of all the admin names
    admin_names = [name for name in admins]

    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form["password"]

        try:
            admin.addUser(new_username, new_password, new_email)
        except ValueError as error:
            print("An error has occurred: " + str(error))
            return redirect(url_for("admin_start", admin_name=admin_name))
        else:
            print("A new user " + new_username + " has been added by " + admin_name)
            return redirect(url_for("admin_start", admin_name=admin_name))

    else:
        return render_template("admin_start.html", admin_name=admin_name, user_names=user_names,
                               user_emails=user_emails, user_balances=user_balances, user_totals=user_totals,
                               product_barcodes=product_barcodes, product_names=product_names,
                               product_prices=product_prices, admin_names=admin_names)


@app.route("/admin_start/<admin_name>/add_user", methods=["POST", "GET"])
def add_user(admin_name):
    password = session.get("password", None)
    admin = Admin(admin_name, password)

    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form["password"]

        try:
            admin.addUser(new_username, new_password, new_email)
        except ValueError as error:
            print("An error has occurred: " + str(error))
            return redirect(url_for("add_user", admin_name=admin_name))
        else:
            print("A new user " + new_username + " has been added by " + admin_name)
            return redirect(url_for("add_user", admin_name=admin_name))

    else:
        return render_template("add_user.html", admin_name=admin_name)


@app.route("/admin_start/<admin_name>/view_history/<user_name>", methods=["POST", "GET"])
def view_history(admin_name, user_name):
    user = User(user_name)

    history = user.getHistory()
    # extract all the lists from the dictionary history
    timestamp = history["time"]
    name = history["name"]
    action = history["action"]
    barcode = history["barcode"]
    product_name = history["product name"]
    amount = history["amount"]

    return render_template("view_history.html", user_name=user_name, timestamp=timestamp, name=name,
                           action=action, barcode=barcode, product_name=product_name, amount=amount)


@app.route("/admin_start/<admin_name>/add_balance/<user_name>", methods=["POST", "GET"])
def add_balance(admin_name, user_name):
    if request.method == "POST":
        password = session.get("password", None)
        admin = Admin(admin_name, password)

        added_balance = request.form["added_balance"]

        try:
            admin.addBalance(user_name, float(added_balance))
        except KeyError as error:
            print("An error occurred: " + str(error))
            return redirect(url_for("add_balance", admin_name=admin_name, user_name=user_name))
        else:
            print("Money added to balance!\tName: " + user_name + " | Amount: " + added_balance + " kr")
            return redirect(url_for("add_balance", admin_name=admin_name, user_name=user_name))

    else:
        return render_template("add_balance.html", admin_name=admin_name, user_name=user_name)


@app.route("/admin_start/<admin_name>/remove_user/<user_name>", methods=["POST", "GET"])
def remove_user(admin_name, user_name):
    if request.method == "POST":
        password = session.get("password", None)
        admin = Admin(admin_name, password)

        user_name_check = request.form["remove_user"]
        decision = request.form["decision"]

        if user_name == user_name_check and decision == "yes":
            try:
                remove_name, email, balance, total = admin.removeUser(user_name)
            except KeyError as error1:
                print(error1)
                return redirect(url_for("remove_user", admin_name=admin_name, user_name=user_name))
            except ValueError as error2:
                print(error2)
                return redirect(url_for("remove_user", admin_name=admin_name, user_name=user_name))
            else:
                print("User removed!\tName: " + remove_name + " | E-mail: " + email + " | Balance: " + str(balance) +
                      " kr | Total spent: " + str(total) + " kr")
                return redirect(url_for("remove_user", admin_name=admin_name, user_name=user_name))

        else:
            print("The admin " + admin_name + " wanted to remove the user " + user_name + " but changed their mind.")
            return redirect(url_for("remove_user", admin_name=admin_name, user_name=user_name))

    else:
        return render_template("remove_user.html", admin_name=admin_name, user_name=user_name)


@app.route("/admin_start/<admin_name>/add_product", methods=["POST", "GET"])
def add_product(admin_name):
    if request.method == "POST":
        password = session.get("password", None)
        admin = Admin(admin_name, password)

        new_barcode = request.form["barcode"]
        new_name = request.form["name"]
        new_price = request.form["price"]

        try:
            admin.addProduct(new_barcode, new_name, float(new_price))
        except ValueError as error:
            print("An error occurred: " + str(error))
            return redirect(url_for("add_product", admin_name=admin_name))
        else:
            print("Product added!\t Barcode: " + new_barcode + "\tName: " + new_name + " | Price: " + str(new_price))
            return redirect(url_for("add_product", admin_name=admin_name))

    else:
        return render_template("add_product.html", admin_name=admin_name)


@app.route("/admin_start/<admin_name>/update_product_price/<product_barcode>/<product_name>", methods=["POST", "GET"])
def update_product_price(admin_name, product_barcode, product_name):
    if request.method == "POST":
        password = session.get("password", None)
        admin = Admin(admin_name, password)

        new_price = request.form["new_price"]

        try:
            old_price = admin.updateProductPrice(product_barcode, float(new_price))
        except KeyError as error:
            print("An error occurred: " + str(error))
            return redirect(url_for("update_product_price", admin_name=admin_name,
                                    product_barcode=product_barcode, product_name=product_name))
        else:
            print("Price updated!\tBarcode: " + product_barcode + " | Name: " + product_name + " | Old price: " +
                  str(old_price) + " | New price: " + str(new_price))
            return redirect(url_for("update_product_price", admin_name=admin_name,
                                    product_barcode=product_barcode, product_name=product_name))
    else:
        return render_template("update_product_price.html", admin_name=admin_name,
                               product_barcode=product_barcode, product_name=product_name)


@app.route("/admin_start/<admin_name>/update_product_name/<product_barcode>/<product_name>", methods=["POST", "GET"])
def update_product_name(admin_name, product_barcode, product_name):
    if request.method == "POST":
        password = session.get("password", None)
        admin = Admin(admin_name, password)

        new_name = request.form["new_name"]

        try:
            old_name = admin.updateProductName(product_barcode, new_name)
        except KeyError as error:
            print("An error occurred: " + str(error))
            return redirect(url_for("update_product_name", admin_name=admin_name,
                                    product_barcode=product_barcode, product_name=product_name))
        else:
            print("Name updated!\tBarcode: " + product_barcode + " | Old name: " +
                  str(old_name) + " | New name: " + str(new_name))
            return redirect(url_for("update_product_name", admin_name=admin_name,
                                    product_barcode=product_barcode, product_name=product_name))
    else:
        return render_template("update_product_name.html", admin_name=admin_name,
                               product_barcode=product_barcode, product_name=product_name)


@app.route("/admin_start/<admin_name>/remove_product/<product_barcode>/<product_name>", methods=["POST", "GET"])
def remove_product(admin_name, product_barcode, product_name):
    if request.method == "POST":
        password = session.get("password", None)
        admin = Admin(admin_name, password)

        decision = request.form["decision"]

        if decision == "yes":
            try:
                barcode, name, price = admin.removeProduct(product_barcode)
            except KeyError as error1:
                print(error1)
                return redirect(url_for("remove_product", admin_name=admin_name, product_barcode=product_barcode,
                                        product_name=product_name))
            else:
                print("Product removed!\tBarcode: " + barcode + " | Name: " + name + " | Price: " + str(price) +
                      " kr")
                return redirect(url_for("remove_product", admin_name=admin_name, product_barcode=product_barcode,
                                        product_name=product_name))
        else:
            print("The admin " + admin_name + " wanted to remove product " + product_barcode +
                  " but changed their mind.")
            return redirect(url_for("remove_product", admin_name=admin_name, product_barcode=product_barcode,
                                    product_name=product_name))

    else:
        return render_template("remove_product.html", admin_name=admin_name,
                               product_barcode=product_barcode, product_name=product_name)


@app.route("/admin_start/<admin_name>/add_admin", methods=["POST", "GET"])
def add_admin(admin_name):
    if request.method == "POST":
        password = session.get("password", None)
        admin = Admin(admin_name, password)

        new_name = request.form["username"]
        new_password = request.form["password"]

        try:
            admin.addAdmin(new_name, new_password)
        except ValueError as error:
            print("An error occurred: " + str(error))
            return redirect(url_for("add_admin", admin_name=admin_name))
        else:
            print("Admin added!\tName: " + new_name)
            return redirect(url_for("add_admin", admin_name=admin_name))

    else:
        return render_template("add_admin.html", admin_name=admin_name)


@app.route("/admin_start/<admin_name>/remove_admin/<remove_admin_name>", methods=["POST", "GET"])
def remove_admin(admin_name, remove_admin_name):
    if request.method == "POST":
        password = session.get("password", None)
        admin = Admin(admin_name, password)

        admin_name_check = request.form["remove_admin"]
        decision = request.form["decision"]

        if remove_admin_name == admin_name_check and decision == "yes":
            try:
                remove_name, email, balance, total = admin.removeUser(remove_admin_name)
            except KeyError as error1:
                print(error1)
                return redirect(url_for("remove_admin", admin_name=admin_name, remove_admin_name=remove_admin_name))
            except ValueError as error2:
                print(error2)
                return redirect(url_for("remove_admin", admin_name=admin_name, remove_admin_name=remove_admin_name))
            else:
                print("Admin removed!\tName: " + remove_name)
                return redirect(url_for("remove_admin", admin_name=admin_name, remove_admin_name=remove_admin_name))

        else:
            print("The admin " + admin_name + " wanted to remove the admin " + remove_admin_name +
                  " but changed their mind.")
            return redirect(url_for("remove_admin", admin_name=admin_name, remove_admin_name=remove_admin_name))

    else:
        return render_template("remove_admin.html", admin_name=admin_name, remove_admin_name=remove_admin_name)


if __name__ == '__main__':
    # todo fix a secret key
    app.secret_key = 'super secret key'

    app.run(debug=True)

