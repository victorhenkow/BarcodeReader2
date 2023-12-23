from flask import Flask, render_template, request, redirect, session, url_for
from back_end import *

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def login():
    message = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # the login privileges, can either be "user" or "admin"
        privileges = request.form["privileges"]

        if privileges == "admin":
            try:
                Admin(username, password)
            except AuthenticationError as error1:
                print(str(error1))
                message = "Wrong username or password"
            except ValueError as error2:
                print(error2)
                message = "Wrong username or password"
            else:
                session["admin_password"] = password
                print("Admin " + username + " has logged in.")
                return redirect(url_for("admin_start", admin_name=username))

        elif privileges == "user":
            try:
                User(username, password)
            except AuthenticationError as error1:
                print(str(error1))
                message = "Wrong username or password"
            except ValueError as error2:
                print(error2)
                message = "Wrong username or password"
            else:
                session["user_password"] = password
                print("The user " + username + " has logged in.")
                return redirect(url_for("user_start", user_name=username))

    return render_template("login.html", message=message)


@app.route("/user_start/<user_name>",  methods=["POST", "GET"])
def user_start(user_name):
    password = session["user_password"]
    user = User(user_name, password)

    email = user.getEmail()
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

    return render_template("user/user_start.html", user_name=user_name, email=email, balance=balance,
                           total_spent=total_spent, timestamp=timestamp, name=name, action=action, barcode=barcode,
                           product_name=product_name, amount=amount, product_barcodes=product_barcodes,
                           product_names=product_names, product_prices=product_prices)


@app.route("/user_start/<user_name>/change_password",  methods=["POST", "GET"])
def change_user_password(user_name):
    message = None

    if request.method == "POST":
        password = session.get("user_password", None)

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        new_password_check = request.form["new_password_check"]

        if not current_password == password:
            print("The current password was incorrect.")
            message = "Incorrect password"
        elif not new_password == new_password_check:
            print("The new passwords did not match.")
            message = "Passwords did not match"
        else:
            user = User(user_name, current_password)
            try:
                user.changePassword(new_password)
            except ValueError as error:
                print(error)
                message = "Input a proper password"
            else:
                print("Password changed by user!\tName: " + user_name)
                # the user needs to log in again to store the correct password
                return redirect(url_for("login"))

    return render_template("user/change_user_password.html", user_name=user_name, message=message)


@app.route("/user_start/<user_name>/change_email",  methods=["POST", "GET"])
def change_user_email(user_name):
    if request.method == "POST":
        password = session.get("user_password", None)

        user = User(user_name, password)
        new_email = request.form["new_email"]
        old_email = user.changeEmail(new_email)
        print("E-mail changed by user!\tName: " + user_name + " | Old e-mail: " + old_email + " | New e-mail: " +
              new_email)
        return redirect(url_for("user_start", user_name=user_name))
    else:
        return render_template("user/change_user_email.html", user_name=user_name)


@app.route("/admin_start/<admin_name>", methods=["POST", "GET"])
def admin_start(admin_name):
    password = session.get("admin_password", None)
    admin = Admin(admin_name, password)

    users = User.getAllUsers()

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

    return render_template("admin/admin_start.html", admin_name=admin_name, user_names=user_names,
                           user_emails=user_emails, user_balances=user_balances, user_totals=user_totals,
                           product_barcodes=product_barcodes, product_names=product_names,
                           product_prices=product_prices, admin_names=admin_names)


@app.route("/admin_start/<admin_name>/add_user", methods=["POST", "GET"])
def add_user(admin_name):
    message = None

    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        new_username = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form["password"]

        try:
            admin.addUser(new_username, new_password, new_email)
        except ValueError as error:
            print(str(error))
            message = str(error)
        else:
            # user added successfully
            print("A new user " + new_username + " has been added by " + admin_name)
            return redirect(url_for("admin_start", admin_name=admin_name))

    return render_template("admin/user_control/add_user.html", admin_name=admin_name, message=message)


@app.route("/admin_start/<admin_name>/view_user_history/<user_name>", methods=["POST", "GET"])
def view_user_history(admin_name, user_name):
    user = User(user_name)

    history = user.getHistory()
    # extract all the lists from the dictionary history
    timestamp = history["time"]
    name = history["name"]
    action = history["action"]
    barcode = history["barcode"]
    product_name = history["product name"]
    amount = history["amount"]

    return render_template("admin/user_control/view_user_history.html", admin_name=admin_name, user_name=user_name,
                           timestamp=timestamp, name=name, action=action, barcode=barcode, product_name=product_name,
                           amount=amount)


@app.route("/admin_start/<admin_name>/add_user_balance/<user_name>", methods=["POST", "GET"])
def add_user_balance(admin_name, user_name):
    message = None
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        added_balance = request.form["added_balance"]
        if added_balance == "":
            message = "Specify an amount"
        else:
            admin.addBalance(user_name, float(added_balance))
            print("Money added to balance!\tName: " + user_name + " | Amount: " + added_balance + " kr")
            return redirect(url_for("admin_start", admin_name=admin_name))

    return render_template("admin/user_control/add_user_balance.html", admin_name=admin_name, user_name=user_name,
                           message=message)


@app.route("/admin_start/<admin_name>/change_user_email/<user_name>", methods=["POST", "GET"])
def admin_change_user_email(admin_name, user_name):
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        new_email = request.form["new_email"]
        old_email = admin.changeUserEmail(user_name, new_email)
        print("User e-mail changed by admin " + admin_name + "!\tName: " + user_name + " | Old e-mail: " + old_email +
              " | New e-mail: " + new_email)
        return redirect(url_for("admin_start", admin_name=admin_name))
    else:
        return render_template("admin/user_control/admin_change_user_email.html", admin_name=admin_name,
                               user_name=user_name)


@app.route("/admin_start/<admin_name>/change_user_password/<user_name>", methods=["POST", "GET"])
def admin_change_user_password(admin_name, user_name):
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        new_password = request.form["new_password"]
        admin.changeUserPassword(user_name, new_password)
        print("User password changed by admin " + admin_name + "!\tName: " + user_name)
        return redirect(url_for("admin_start", admin_name=admin_name))
    else:
        return render_template("admin/user_control/admin_change_user_password.html", admin_name=admin_name,
                               user_name=user_name)


@app.route("/admin_start/<admin_name>/remove_user/<user_name>", methods=["POST", "GET"])
def remove_user(admin_name, user_name):
    message = None
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        user_name_check = request.form["remove_user"]
        decision = request.form["decision"]

        if user_name == user_name_check and decision == "yes":
            remove_name, email, balance, total = admin.removeUser(user_name)
            print("User removed!\tName: " + remove_name + " | E-mail: " + email + " | Balance: " + str(balance) +
                  " kr | Total spent: " + str(total) + " kr")
            return redirect(url_for("admin_start", admin_name=admin_name))

        else:
            message = "Check failed"
    return render_template("admin/user_control/remove_user.html", admin_name=admin_name,
                           user_name=user_name, message=message)


@app.route("/admin_start/<admin_name>/add_product", methods=["POST", "GET"])
def add_product(admin_name):
    message = None
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        new_barcode = request.form["barcode"]
        new_name = request.form["name"]
        new_price = request.form["price"]

        try:
            admin.addProduct(new_barcode, new_name, float(new_price))
        except ValueError as error:
            print(str(error))
            message = str(error)
        else:
            # product added successfully
            print("Product added!\t Barcode: " + new_barcode + "\tName: " + new_name + " | Price: " + str(new_price))
            return redirect(url_for("admin_start", admin_name=admin_name))

    return render_template("admin/product_control/add_product.html", admin_name=admin_name, message=message)


@app.route("/admin_start/<admin_name>/update_product_price/<product_barcode>/<product_name>", methods=["POST", "GET"])
def change_product_price(admin_name, product_barcode, product_name):
    message = None
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        new_price = request.form["new_price"]
        if new_price == "":
            message = "Specify a price"
        else:
            old_price = admin.changeProductPrice(product_barcode, float(new_price))
            print("Price changed!\tBarcode: " + product_barcode + " | Name: " + product_name + " | Old price: " +
                  str(old_price) + " | New price: " + str(new_price))
            return redirect(url_for("admin_start", admin_name=admin_name))

    return render_template("admin/product_control/change_product_price.html", admin_name=admin_name,
                           product_barcode=product_barcode, product_name=product_name, message=message)


@app.route("/admin_start/<admin_name>/update_product_name/<product_barcode>/<product_name>", methods=["POST", "GET"])
def change_product_name(admin_name, product_barcode, product_name):
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        new_name = request.form["new_name"]
        old_name = admin.changeProductName(product_barcode, new_name)
        print("Name updated!\tBarcode: " + product_barcode + " | Old name: " +
              str(old_name) + " | New name: " + str(new_name))
        return redirect(url_for("admin_start", admin_name=admin_name))
    else:
        return render_template("admin/product_control/change_product_name.html", admin_name=admin_name,
                               product_barcode=product_barcode, product_name=product_name)


@app.route("/admin_start/<admin_name>/remove_product/<product_barcode>/<product_name>", methods=["POST", "GET"])
def remove_product(admin_name, product_barcode, product_name):
    message = None
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        decision = request.form["decision"]

        if decision == "yes":
            barcode, name, price = admin.removeProduct(product_barcode)

            print("Product removed!\tBarcode: " + barcode + " | Name: " + name + " | Price: " + str(price) + " kr")
            return redirect(url_for("admin_start", admin_name=admin_name))
        else:
            print("The admin " + admin_name + " wanted to remove product " + product_barcode +
                  " but changed their mind.")
            message = "Check failed"

    return render_template("admin/product_control/remove_product.html", admin_name=admin_name,
                           product_barcode=product_barcode, product_name=product_name, message=message)


@app.route("/admin_start/<admin_name>/add_admin", methods=["POST", "GET"])
def add_admin(admin_name):
    message = None
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        new_name = request.form["username"]
        new_password = request.form["password"]

        try:
            admin.addAdmin(new_name, new_password)
        except ValueError as error:
            print("An error occurred: " + str(error))
            message = str(error)
        else:
            # admin added successfully
            print("Admin added!\tName: " + new_name)
            return redirect(url_for("admin_start", admin_name=admin_name))

    return render_template("admin/admin_control/add_admin.html", admin_name=admin_name, message=message)


# Note that an admin cannot remove itself, this would give an error and could result in there being no admins left.
# This is controlled by not giving a remove link to the logged in admin in admin_start.html
@app.route("/admin_start/<admin_name>/remove_admin/<remove_admin_name>", methods=["POST", "GET"])
def remove_admin(admin_name, remove_admin_name):
    message = None
    if request.method == "POST":
        password = session.get("admin_password", None)
        admin = Admin(admin_name, password)

        admin_name_check = request.form["remove_admin"]
        decision = request.form["decision"]

        if remove_admin_name == admin_name_check and decision == "yes":
            remove_name = admin.removeAdmin(remove_admin_name)

            print("Admin removed!\tName: " + remove_name)
            return redirect(url_for("admin_start", admin_name=admin_name))

        else:
            print("The admin " + admin_name + " wanted to remove the admin " + remove_admin_name +
                  " but changed their mind.")
            message = "Check failed"

    return render_template("admin/admin_control/remove_admin.html", admin_name=admin_name,
                           remove_admin_name=remove_admin_name, message=message)


@app.route("/admin_start/<admin_name>/change_password/", methods=["POST", "GET"])
def change_admin_password(admin_name):
    message = None
    if request.method == "POST":
        password = session.get("admin_password", None)
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        new_password_check = request.form["new_password_check"]

        if not current_password == password:
            print("The current password was incorrect.")
            message = "Incorrect password"
        elif not new_password == new_password_check:
            print("The new passwords did not match.")
            message = "New passwords did not match"
        else:
            # password changed successfully
            admin = Admin(admin_name, password)
            admin.changePassword(new_password)
            print("Password changed by admin!\tName: " + admin_name)
            # the admin needs to log in again to store the correct password
            return redirect(url_for("login"))

    return render_template("admin/admin_control/change_admin_password.html", admin_name=admin_name,
                           message=message)


if __name__ == '__main__':
    # todo fix a secret key
    app.secret_key = 'super secret key'

    app.run(debug=True)
