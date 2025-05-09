from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDList
from kivymd.toast import toast
from firebase_config import db
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty, ListProperty


class Orders(Screen):
    status_filter = StringProperty("All")
    status_options = ListProperty(["All", "Pending", "Preparing", "Ready", "Completed", "Cancelled"])

    def on_pre_enter(self):
        self.setup_filter_menu()
        self.load_orders()
        self.orders_listener = db.child("orders").stream(self.update_orders)

    def on_enter(self, *args):
        self.load_orders()

    def setup_filter_menu(self):
        menu_items = [
            {
                "text": status,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=status: self.filter_orders(x),
            } for status in self.status_options
        ]
        self.filter_menu = MDDropdownMenu(
            caller=self.ids.filter_button,
            items=menu_items,
            width_mult=4,
            max_height=dp(200),
            border_margin=dp(10),
            radius=[dp(10)],
        )

    def filter_orders(self, status):
        self.status_filter = status
        self.filter_menu.dismiss()
        self.load_orders()

    def update_orders(self, message):
        self.load_orders()

    def load_orders(self):
        self.ids.orders_list.clear_widgets()

        try:
            orders_data = db.child("orders").get().val()
            if not orders_data:
                self.show_empty_state()
                return

            filtered_orders = {
                oid: order for oid, order in orders_data.items()
                if self.status_filter == "All" or order.get("status") == self.status_filter
            }

            if not filtered_orders:
                self.show_empty_state(filtered=True)
                return

            for order_id, order in filtered_orders.items():
                self.add_order_card(order_id, order)

        except Exception as e:
            self.show_error_state(e)

    def add_order_card(self, order_id, order):
        status = order.get("status", "Pending")
        status_colors = {
            "Completed": ("#E8F5E9", "#2E7D32"),
            "Cancelled": ("#FFEBEE", "#C62828"),
            "Pending": ("#FFF8E1", "#FF8F00"),
            "Preparing": ("#E3F2FD", "#1565C0"),
            "Ready": ("#E0F7FA", "#00838F")
        }
        bg_color, text_color = status_colors.get(status, ("#F3E5F5", "#7B1FA2"))

        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True,
            elevation=3,
            md_bg_color=get_color_from_hex(bg_color),
            radius=[dp(15)],
            padding=dp(15),
            spacing=dp(8),
        )

        card.add_widget(MDLabel(
            text=f"[b]Order #{order_id}[/b]",
            markup=True,
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(28)
        ))

        user_id = order.get("user_id")
        user_data = db.child("users").child(user_id).get().val() if user_id else {}

        customer_name = user_data.get("name", "Unknown User")
        customer_phone = user_data.get("phone", "N/A")

        card.add_widget(MDLabel(
            text=f"[b]Customer:[/b] {customer_name}  |  [b]Phone:[/b] {customer_phone}",
            markup=True,
            font_style="Body2",
            size_hint_y=None,
            height=dp(20)
        ))

        items = order.get('items', {})
        items_detail = "\n".join([f"• {item['name']} x{item['quantity']}" for item in items.values()])
        card.add_widget(MDLabel(
            text=f"[b]Items Ordered:[/b]\n{items_detail}",
            markup=True,
            font_style="Body2",
            size_hint_y=None,
            height=dp(20 + 18 * len(items))
        ))

        method = order.get("delivery_method", "pickup").capitalize()
        address = order.get("delivery_address", "N/A") if method == "Delivery" else "N/A"

        delivery_text = f"[b]Method:[/b] {method}"
        if method == "Delivery":
            delivery_text += f"\n[b]Address:[/b] {address}"

        card.add_widget(MDLabel(
            text=delivery_text,
            markup=True,
            font_style="Body2",
            size_hint_y=None,
            height=dp(40 if method == "Delivery" else 20)
        ))

        card.add_widget(MDLabel(
            text=f"[b]Payment:[/b] {order.get('payment_method', 'N/A').capitalize()}",
            markup=True,
            font_style="Body2",
            size_hint_y=None,
            height=dp(20)
        ))

        card.add_widget(MDLabel(
            text=f"[b]Placed:[/b] {order.get('timestamp', 'N/A')}",
            markup=True,
            font_style="Caption",
            size_hint_y=None,
            height=dp(18),
            theme_text_color="Secondary"
        ))

        card.add_widget(MDLabel(
            text=f"[b]Total:[/b] ₱{order.get('total', 0):.2f}     [b]Status:[/b] [color={text_color}]{status.upper()}[/color]",
            markup=True,
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))

        if status in ["Pending", "Preparing", "Ready"]:
            self.add_action_buttons(card, order_id, status)

        card.height = card.minimum_height

        self.ids.orders_list.add_widget(card)

    def add_action_buttons(self, card, order_id, current_status):
        actions = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(10),
            padding=[0, dp(8), 0, 0])

        status_flow = {
            "Pending": "Preparing",
            "Preparing": "Ready",
            "Ready": "Completed"
        }

        if current_status in status_flow:
            next_status = status_flow[current_status]
            actions.add_widget(MDRaisedButton(
                text=f"MARK AS {next_status.upper()}",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#FFFFFF"),
                md_bg_color=get_color_from_hex("#2E7D32"),
                size_hint_x=0.7,
                on_release=lambda x, oid=order_id, ns=next_status: self.update_order_status(oid, ns)))

        if current_status != "Ready":
            actions.add_widget(MDRaisedButton(
                text="CANCEL",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#FFFFFF"),
                md_bg_color=get_color_from_hex("#C62828"),
                size_hint_x=0.3,
                on_release=lambda x, oid=order_id: self.confirm_cancel(oid)))

        card.add_widget(actions)

    def show_empty_state(self, filtered=False):
        message = "No orders found" if not filtered else f"No {self.status_filter} orders"
        self.ids.orders_list.add_widget(MDLabel(
            text=message,
            halign="center",
            valign="center",
            font_style="H5",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(200)))

    def show_error_state(self, error):
        self.ids.orders_list.add_widget(MDLabel(
            text="Failed to load orders",
            halign="center",
            valign="center",
            font_style="H5",
            theme_text_color="Error",
            size_hint_y=None,
            height=dp(200)))
        print("Order loading error:", error)

    def confirm_cancel(self, order_id):
        self.dialog = MDDialog(
            title="[size=20][b]Confirm Cancellation[/b][/size]",
            text="[size=16]Are you sure you want to cancel this order?[/size]",
            buttons=[
                MDFlatButton(
                    text="NO",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex("#757575"),
                    on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(
                    text="YES",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex("#FFFFFF"),
                    md_bg_color=get_color_from_hex("#C62828"),
                    on_release=lambda x: [self.update_order_status(order_id, "Cancelled"), self.dialog.dismiss()]),
            ],
            radius=[dp(20), dp(7), dp(20), dp(7)],
        )
        self.dialog.open()

    def update_order_status(self, order_id, new_status):
        try:
            db.child("orders").child(order_id).update({"status": new_status})
            toast(f"Order #{order_id} updated to {new_status}")
            self.load_orders()
        except Exception as e:
            toast("Failed to update status")
            print(f"Error updating status: {e}")

    def on_leave(self):
        if hasattr(self, 'orders_listener'):
            self.orders_listener.close()
        if hasattr(self, 'filter_menu'):
            self.filter_menu.dismiss()