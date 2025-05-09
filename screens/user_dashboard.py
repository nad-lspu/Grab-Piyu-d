from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from firebase_config import auth, db
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivy.clock import Clock


class UserDashboard(MDScreen):
    def on_pre_enter(self, *args):
        self.load_user_data()
        self.load_order_history()

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.load_order_history(), 0.5)

    def load_user_data(self):
        try:
            user = auth.current_user
            if user:
                user_id = user['localId']
                user_data = db.child("users").child(user_id).get().val()
                if user_data:
                    self.ids.user_name.text = user_data.get("name", "No Name")
                    self.ids.user_email.text = user_data.get("email", "No Email")
        except Exception as e:
            toast(f"Error loading data: {e}")

    def load_order_history(self):
        try:
            user = auth.current_user
            if user:
                user_id = user['localId']
                orders = db.child("orders").order_by_child("user_id").equal_to(user_id).get().val()
                self.ids.order_history.clear_widgets()

                if orders:
                    sorted_orders = sorted(
                        orders.items(),
                        key=lambda x: x[1].get('timestamp', ''),
                        reverse=True
                    )

                    for order_id, order_data in sorted_orders:
                        self.add_order_card(order_id, order_data)
                else:
                    self.show_no_orders_message()

        except Exception as e:
            toast(f"Error loading orders: {e}")

    def add_order_card(self, order_id, order_data):
        display_id = order_data.get('order_id', order_id[-6:])
        status = order_data.get('status', 'unknown').capitalize()
        total = f"₱{order_data.get('total', 0):.2f}"
        date = order_data.get('timestamp', '')[:10]

        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_y=None,
            height=dp(120),
            ripple_behavior=True,
            radius=[8],
            md_bg_color=[0.98, 0.98, 0.98, 1]
        )

        box_top = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        box_top.add_widget(MDLabel(
            text=f"Order #{display_id}",
            font_style="Subtitle1",
            theme_text_color="Primary",
            bold=True,
            size_hint_x=0.7
        ))
        box_top.add_widget(MDLabel(
            text=status,
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=self.get_status_color(status.lower()),
            halign="right",
            size_hint_x=0.3
        ))
        card.add_widget(box_top)

        box_middle = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        box_middle.add_widget(MDLabel(
            text=f"Total: {total}",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_x=0.7
        ))
        box_middle.add_widget(MDLabel(
            text=date,
            font_style="Body2",
            theme_text_color="Secondary",
            halign="right",
            size_hint_x=0.3
        ))
        card.add_widget(box_middle)

        if order_data.get('delivery_method') == 'delivery':
            method = f"Delivery to: {order_data.get('delivery_address', '')}"
        else:
            method = f"Pickup at: {order_data.get('pickup_location', '')}"

        card.add_widget(MDLabel(
            text=method,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20)
        ))

        card.bind(on_release=lambda instance, oid=order_id: self.view_order_details(oid))
        self.ids.order_history.add_widget(card)

    def get_status_color(self, status):
        colors = {
            'pending': [0.9, 0.5, 0.1, 1],
            'preparing': [0.2, 0.5, 0.8, 1],
            'completed': [0.12, 0.65, 0.32, 1],
            'cancelled': [0.9, 0.2, 0.2, 1]
        }
        return colors.get(status, [0.5, 0.5, 0.5, 1])

    def show_no_orders_message(self):
        self.ids.order_history.add_widget(MDLabel(
            text="No orders found.",
            halign="center",
            valign="middle",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(50)
        ))

    def view_order_details(self, order_id):
        toast(f"Showing details for order {order_id}")

    def navigate_to_menu(self):
        self.manager.transition.direction = 'left'
        self.manager.current = "menu_screen"

    def logout(self):
        auth.current_user = None
        self.manager.transition.direction = 'right'
        self.manager.current = "login_screen"