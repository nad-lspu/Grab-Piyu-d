from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineListItem
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.app import App
from kivy.metrics import dp
from firebase_config import db, auth
import uuid
from datetime import datetime
from kivy.clock import Clock

class CheckoutScreen(MDScreen):
    delivery_method = "delivery"
    dialog = None
    user_phone = ""

    def on_enter(self):
        """Load order summary when screen is entered"""
        self.load_order_summary()
        self.load_user_data()
        self.ids.delivery_address.text = ""
        self.ids.special_instructions.text = ""

        self.set_delivery_method("delivery")

    def on_pre_enter(self):
        """Set focus to delivery address when screen is about to be shown"""
        Clock.schedule_once(self.focus_delivery_address, 0.1)

    def focus_delivery_address(self, dt):
        """Set focus to delivery address field"""
        self.ids.delivery_address.focus = True

    def load_user_data(self):
        try:
            if auth.current_user:
                user_data = db.child("users").order_by_child("email").equal_to(auth.current_user["email"]).get().val()

                if user_data:
                    user_id = list(user_data.keys())[0]
                    user = user_data[user_id]

                    self.user_phone = user.get("phone", "")

                    self.ids.contact_info.text = f"Your Contact No.: {self.user_phone}"
                else:
                    self.ids.contact_info.text = "Contact information not found"
            else:
                self.ids.contact_info.text = "Sign in to use your saved contact info"
        except Exception as e:
            print(f"Error loading user data: {str(e)}")
            self.ids.contact_info.text = "Error loading contact information"

    def load_order_summary(self):
        self.ids.order_summary_list.clear_widgets()
        app = App.get_running_app()
        cart = app.cart

        if not cart:
            toast("Your cart is empty!")
            self.go_back()
            return

        total = 0
        for item_id, item in cart.items():
            item_name = item["name"]
            quantity = item["quantity"]
            price = item["price"]
            subtotal = quantity * price
            total += subtotal

            summary_item = TwoLineListItem(
                text=f"{item_name} x{quantity}",
                secondary_text=f"₱{subtotal:.2f}",
                theme_text_color="Primary",
                secondary_theme_text_color="Custom",
                secondary_text_color=[0.9, 0.5, 0.1, 1]
            )
            self.ids.order_summary_list.add_widget(summary_item)

        self.ids.checkout_total.text = f"₱{total:.2f}"

    def set_delivery_method(self, method):
        self.delivery_method = method

        if method == "delivery":
            self.ids.delivery_checkbox.active = True
            self.ids.pickup_checkbox.active = False
            self.ids.delivery_address_label.text = "Delivery Address"
            self.ids.delivery_address.hint_text = "Enter your delivery address"
            self.ids.delivery_address.text = ""
            self.ids.delivery_address.disabled = False
            self.ids.delivery_address.focus = True
            self.ids.pickup_time_section.opacity = 0
            self.ids.pickup_time_section.height = 0
        else:
            self.ids.delivery_checkbox.active = False
            self.ids.pickup_checkbox.active = True
            self.ids.delivery_address_label.text = "Pickup Location"
            self.ids.delivery_address.hint_text = ""
            self.ids.delivery_address.text = "CIT Building 1st Floor (Default)"
            self.ids.delivery_address.disabled = True
            self.ids.pickup_time_section.opacity = 1
            self.ids.pickup_time_section.height = dp(70)

    def validate_form(self):
        if not self.ids.delivery_address.text.strip():
            if self.delivery_method == "delivery":
                toast("Please enter your delivery address")
            else:
                toast("Please select a pickup location")
            return False

        if not self.user_phone:
            toast("Contact information not available")
            return False

        if self.delivery_method == "pickup" and not self.ids.pickup_time.text.strip():
            toast("Please select a pickup time")
            return False

        return True

    def place_order(self):
        if not self.validate_form():
            return

        app = App.get_running_app()
        if not app.cart:
            toast("Your cart is empty")
            return

        order_data = {
            "user_id": auth.current_user["localId"] if auth.current_user else "guest",
            "items": app.cart,
            "delivery_method": self.delivery_method,
            "contact_number": self.user_phone,
            "special_instructions": self.ids.special_instructions.text.strip(),
            "payment_method": "cash",
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "order_id": str(uuid.uuid4())[:8].upper()
        }

        if self.delivery_method == "delivery":
            order_data["delivery_address"] = self.ids.delivery_address.text.strip()
        else:
            order_data["pickup_location"] = self.ids.delivery_address.text.strip()
            order_data["pickup_time"] = self.ids.pickup_time.text.strip()

        total = sum(item["price"] * item["quantity"] for item in app.cart.values())
        order_data["total"] = total

        self.show_order_confirmation(order_data)

    def show_order_confirmation(self, order_data):
        if self.dialog:
            self.dialog.dismiss()

        order_id = order_data["order_id"]
        total = order_data["total"]

        if order_data["delivery_method"] == "delivery":
            method_text = f"Delivery to: {order_data['delivery_address']}"
        else:
            method_text = f"Pickup at: {order_data['pickup_location']}\nTime: {order_data['pickup_time']}"

        self.dialog = MDDialog(
            title="Confirm Your Order",
            text=f"Order #{order_id}\nTotal: ₱{total:.2f}\n{method_text}\nPayment: Cash on Delivery\n\nProceed with your order?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=[0.5, 0.5, 0.5, 1],
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="CONFIRM",
                    theme_text_color="Custom",
                    text_color=[0.12, 0.65, 0.32, 1],
                    on_release=lambda x: self.confirm_order(order_data)
                ),
            ],
        )
        self.dialog.open()

    def confirm_order(self, order_data):
        self.dialog.dismiss()

        try:
            db.child("orders").child(order_data["order_id"]).set(order_data)

            app = App.get_running_app()
            app.last_order_id = order_data["order_id"]

            app.cart = {}

            toast(f"Order #{order_data['order_id']} placed successfully!")

            self.manager.transition.direction = 'left'
            self.manager.current = "order_confirmation"

        except Exception as e:
            toast(f"Error placing order: {str(e)}")

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = "cart_screen"