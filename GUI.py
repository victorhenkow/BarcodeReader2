import tkinter as tk
from back_end import *
import read_and_write as rw


class Windows(tk.Tk):
    def __init__(self, first_page, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # importing the settings file to a dictionary
        # every setting is a list, so it needs to be called by settings["whatever option"][0]
        settings = self.getSettings()

        self.wm_title(settings["title"])
        self.geometry("600x400")

        # creating a frame and assigning it to container
        self.container = tk.Frame(self, height=400, width=600)
        # specifying the region where the frame is packed in root
        self.container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_page(first_page)

    def show_page(self, page, *args):
        frame = page(self.container, self, *args)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    @staticmethod
    def getSettings():
        return rw.read_settings()


class SplashGreen(tk.Frame):
    def __init__(self, parent, controller, *args):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        settings = Windows.getSettings()

        self.configure(bg="green")

        splash_time = int(settings["splash time"])

        self.timeout = self.after(splash_time, lambda: self.controller.show_page(*args))


class SplashRed(tk.Frame):
    def __init__(self, parent, controller, *args):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.args = args

        settings = Windows.getSettings()

        self.configure(bg="red")

        splash_time = int(settings["splash time"])

        self.timeout = self.after(splash_time, lambda: self.controller.show_page(*args))


class ScanUserPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.login)

        self.name = tk.StringVar()  # the name which the user inputs

        settings = Windows.getSettings()
        self.font_size = settings["font size"]
        self.font = settings["font"]
        self.bg_color = settings["background color"]
        self.fg_color = settings["foreground color"]
        self.pad = settings["padding"]

        self.createGraphics()

    def createGraphics(self):
        self.configure(bg=self.bg_color)

        name_label = tk.Label(self, text="Username", font=(self.font, self.font_size), bg=self.bg_color, fg=self.fg_color, pady=self.pad)
        name_entry = tk.Entry(self, textvariable=self.name, font=(self.font, self.font_size), bg=self.fg_color, fg=self.bg_color)

        #submit_button = tk.Button(self, text="Submit", command=self.login, font=(self.font, self.font_size), bg="black", fg="red")

        name_entry.focus_set()

        name_label.pack()
        name_entry.pack()
        #submit_button.pack()

    def login(self, event=None):
        name = self.name.get()

        try:
            # check if the user exist
            user = User(name)
        except ValueError as error:
            print(str(error))
            self.controller.show_page(SplashRed, ScanUserPage)
        else:
            print("User " + name + " has started a purchase.")
            settings = Windows.getSettings()
            self.controller.show_page(SplashGreen, ScanProductPage, user, int(settings["first timeout"]))


class ScanProductPage(tk.Frame):
    def __init__(self, parent, controller, user, timeout):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.buy)

        settings = Windows.getSettings()
        self.font_size = settings["font size"]
        self.accent_font_size = settings["accent font size"]
        self.font = settings["font"]
        self.pad = settings["padding"]
        self.bg_color = settings["background color"]
        self.fg_color = settings["foreground color"]
        self.history_number = int(settings["history displayed when buy"])
        self.timeout_2 = int(settings["second timeout"])

        self.user = user  # the user who is going to buy
        self.username = self.user.getName()
        self.balance = self.user.getBalance()
        self.total = self.user.getTotal()
        self.history = self.user.getHistory()

        self.barcode = tk.StringVar()  # the name which the user inputs

        # a timeout for buying
        self.timeout = self.after(timeout, lambda reason=", timed out": self.back(reason))
        self.timer = self.after(0, self.countdown)
        self.count = int(timeout / 1000 + 1)  # needs to have +1 since countdown always takes -1 from self.count
        self.count_var = tk.IntVar()

        self.createGraphics()

    def createGraphics(self):
        self.configure(bg=self.bg_color)

        barcode_title = tk.Label(self, text="Welcome " + self.username + "!\nScan a product barcode.", bg=self.bg_color, fg=self.fg_color, font=(self.font, self.font_size), pady=self.pad)
        barcode_label = tk.Label(self, text="Balance: " + str(self.balance) + " kr", bg=self.bg_color, fg=self.fg_color, font=(self.font, self.accent_font_size), pady=self.pad)
        barcode_entry = tk.Entry(self, textvariable=self.barcode, font=(self.font, self.font_size), bg=self.fg_color, fg=self.bg_color)
        countdown_label = tk.Label(self, textvariable=self.count_var, bg=self.bg_color, fg=self.fg_color, font=(self.font, self.font_size), pady=self.pad)
        #submit_button = tk.Button(self, text="Submit", command=self.buy)

        barcode_entry.focus_set()

        barcode_title.pack()
        barcode_label.pack()
        barcode_entry.pack()
        countdown_label.pack()
        #submit_button.pack()

        # display the last 4 purchases
        history_title_label = tk.Label(self, text="\n History \n----------------------", bg=self.bg_color, fg=self.fg_color, font=(self.font, self.accent_font_size))
        history_title_label.pack()
        try:  # The user may not have four items in its history
            for i in range(self.history_number):
                timestamp = self.history["time"][-i]
                barcode = self.history["barcode"][-i]
                name = self.history["product name"][-i]
                price = str(self.history["amount"][-i])
                history_label = tk.Label(self, text=timestamp + "\n" + barcode + ", " + name + ", " + price + " kr \n\n", bg=self.bg_color, fg=self.fg_color, font=(self.font, self.accent_font_size))

                history_label.pack()
        except IndexError:
            pass  # No problem if the user does not have enough purchase history, just don't display it

    def countdown(self):
        self.count -= 1
        self.count_var.set(self.count)

        # counts down every second
        self.timer = self.after(1000, self.countdown)

    def back(self, reason=""):
        self.after_cancel(self.timer)

        print("Purchase cancelled" + reason)
        self.controller.show_page(ScanUserPage)

    def buy(self, event=None):
        barcode = self.barcode.get()

        if barcode == "000":
            self.back(" by user.")
        else:
            try:
                product = Product(barcode)
                name = product.getName()
                price = product.getPrice()
            except ValueError as error:
                print(str(error))
                self.after_cancel(self.timeout)
                self.after_cancel(self.timer)
                self.controller.show_page(SplashRed, ScanProductPage, self.user, self.timeout_2)
            else:
                self.user.buy(barcode)

                balance = str(self.user.getBalance())
                total = str(self.user.getTotal())

                print("Purchase successful!\tItem barcode: " + barcode + " | Item name: " + name + " | Item price: "
                      + str(price) + " kr | User balance: " + str(balance) + " kr | User total spent: " + str(total) +
                      " kr")

                # after you have bought something you have time to buy more things without scanning the username again
                # first the old timeout needs to be cancelled, then we set a new lower time one for each new purchase
                self.after_cancel(self.timeout)
                self.after_cancel(self.timer)
                self.controller.show_page(SplashGreen, ScanProductPage, self.user, self.timeout_2)


if __name__ == "__main__":
    testObj = Windows(ScanUserPage)
    testObj.mainloop()
