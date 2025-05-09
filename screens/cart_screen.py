from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.toast import toast
from kivy.metrics import dp
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty


class CartItem(MDCard):
    item_id = StringProperty("")
    item_name = StringProperty("")
    quantity = NumericProperty(1)
    price = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CartScreen(MDScreen):
    def on_enter(self):
        self.load_cart()

    def load_cart(self):
        self.ids.cart_list.clear_widgets()
        app = App.get_running_app()
        cart = app.cart

        item_count = sum(item["quantity"] for item in cart.values()) if cart else 0
        self.ids.cart_item_count.text = f"({item_count} items)"

        if not cart:
            self.ids.cart_list.add_widget(MDLabel(
                text="Your cart is empty.",
                halign="center",
                theme_text_color="Hint",
                font_style="Body1",
                padding=[0, dp(20)]
            ))
            self.ids.cart_total.text = "₱0.00"
            return

        total = 0
        for item_id, item in cart.items():
            item_name = item["name"]
            quantity = item["quantity"]
            price = item["price"]
            subtotal = quantity * price
            total += subtotal

            cart_item = CartItem(
                item_id=item_id,
                item_name=item_name,
                quantity=quantity,
                price=price
            )

            self.ids.cart_list.add_widget(cart_item)

        self.ids.cart_total.text = f"₱{total:.2f}"

    def modify_quantity(self, item_id, delta):
        app = App.get_running_app()
        cart = app.cart
        if item_id in cart:
            cart[item_id]["quantity"] += delta
            if cart[item_id]["quantity"] <= 0:
                del cart[item_id]
            self.load_cart()

    def remove_item(self, item_id):
        app = App.get_running_app()
        if item_id in app.cart:
            del app.cart[item_id]
        self.load_cart()

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = "menu_screen"

    def proceed_to_checkout(self):
        app = App.get_running_app()
        if not app.cart:
            toast("Your cart is empty. Please add items first.")
        else:
            self.manager.transition.direction = 'left'
            self.manager.current = "checkout_screen"
            return

