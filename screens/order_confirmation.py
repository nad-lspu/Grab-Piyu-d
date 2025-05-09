from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivy.metrics import dp
from firebase_config import db, auth
from kivy.properties import StringProperty


class OrderConfirmScreen(MDScreen):
    order_title = StringProperty("Order Confirmation")
    order_number = StringProperty("")
    order_status = StringProperty("Processing your order...")
    delivery_info = StringProperty("")
    estimated_time = StringProperty("Estimated time: 30-45 minutes")
    payment_info = StringProperty("Payment method: Cash on Delivery")
    total_amount = StringProperty("₱0.00")

    def on_enter(self):
        app = App.get_running_app()

        self.order_title = "Order Confirmation"
        self.order_number = "Thank you for your order!"
        self.order_status = "Your order has been received."
        self.delivery_info = "You will receive updates soon."
        self.estimated_time = "Estimated time: 30-45 minutes"
        self.payment_info = "Payment method: Cash on Delivery"
        self.total_amount = "₱0.00"

        if hasattr(app, 'last_order_id'):
            self.load_order_details(app.last_order_id)

    def load_order_details(self, order_id):
        try:
            order_data = db.child("orders").child(order_id).get().val()

            if order_data:
                self.order_number = f"Order #{order_data.get('order_id', '')}"
                self.order_status = f"Status: {order_data.get('status', 'Processing').capitalize()}"
                self.estimated_time = "Estimated time: 30-45 minutes"

                payment_method = order_data.get('payment_method', 'cash').capitalize()
                self.payment_info = f"Payment method: {payment_method}"

                total = float(order_data.get('total', 0))
                self.total_amount = f"₱{total:.2f}"

                if order_data.get('delivery_method') == 'delivery':
                    self.delivery_info = (
                        f"Delivery to: {order_data.get('delivery_address', '')}\n"
                        f"Contact: {order_data.get('contact_number', '')}"
                    )
                else:
                    self.delivery_info = (
                        f"Pickup from: {order_data.get('pickup_location', '')}\n"
                        f"Pickup time: {order_data.get('pickup_time', '')}\n"
                        f"Contact: {order_data.get('contact_number', '')}"
                    )

            else:
                self.order_number = f"Order #{order_id}"
                self.order_status = "Your order has been received."
                self.delivery_info = "Thank you for your order!"

        except Exception as e:
            print(f"Error loading order details: {str(e)}")
            self.order_status = "Error loading order details."
            self.delivery_info = "Please check your order history later."

    def go_to_menu(self):
        app = App.get_running_app()
        if hasattr(app, 'last_order_id'):
            del app.last_order_id

        self.manager.transition.direction = 'right'
        self.manager.current = "menu_screen"