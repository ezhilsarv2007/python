"""Q5: Canteen order functions and variable scope."""


def add_item_buggy(item, order=[]):
    order.append(item)
    return order


def add_item(item, order=None):
    if order is None:
        order = []
    order.append(item)
    return order


def bill(item_price, quantity=1, gst_rate=0.05):
    subtotal = item_price * quantity
    gst = subtotal * gst_rate
    total = subtotal + gst
    return total, gst


def scope_demo():
    message = "local message"

    def change_local():
        message = "new local message"
        print("Inside change_local:", message)

    change_local()
    print("Outside function:", message)


def nonlocal_demo():
    count = 0

    def increase():
        nonlocal count
        count += 1
        return count

    print("Nonlocal count:", increase())
    print("Nonlocal count:", increase())


GLOBAL_NOTE = "original global value"


def global_demo():
    global GLOBAL_NOTE
    GLOBAL_NOTE = "changed using global keyword"


print("MUTABLE DEFAULT BUG")
print(add_item_buggy("Tea"), add_item_buggy("Vada"))
print("Stored default:", add_item_buggy.__defaults__)

print("\nCORRECTED ORDERS")
customer_one = add_item("Tea")
customer_two = add_item("Vada")
customer_three = add_item("Sandwich")
print("Customer 1:", customer_one)
print("Customer 2:", customer_two)
print("Customer 3:", customer_three)

print("\nBILL")
total, gst = bill(100, quantity=2)
print("Total:", round(total, 2), "| GST:", round(gst, 2))

print("\nSCOPE")
scope_demo()
nonlocal_demo()
print("Before global function:", GLOBAL_NOTE)
global_demo()
print("After global function:", GLOBAL_NOTE)
