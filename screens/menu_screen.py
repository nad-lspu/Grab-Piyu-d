from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast
from firebase_config import db, auth
from kivy.metrics import dp
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty


class MenuItem(MDCard):
    name = StringProperty("")
    price = NumericProperty(0)
    description = StringProperty("")
    item_id = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.size_hint_y = None
        self.height = dp(180)
        self.ripple_behavior = True
        self.radius = [10]
        self.elevation = 1
        self.md_bg_color = [0.98, 0.98, 0.98, 1]

    def add_to_cart(self):
        app = App.get_running_app()
        if self.item_id in app.cart:
            app.cart[self.item_id]["quantity"] += 1
        else:
            app.cart[self.item_id] = {
                "name": self.name,
                "quantity": 1,
                "price": self.price
            }
        toast(f"Added {self.name} to cart")


class MenuScreen(MDScreen):
    def on_enter(self):
        self.load_menu()

    def load_menu(self):
        try:
            self.ids.menu_list.clear_widgets()
            self.ids.menu_list.add_widget(MDLabel(
                text="Loading menu items...",
                halign="center",
                theme_text_color="Secondary"
            ))

            menu_items = db.child("menu").get().val()
            self.ids.menu_list.clear_widgets()

            if not menu_items:
                self.ids.menu_list.add_widget(MDLabel(
                    text="No menu items available.",
                    halign="center",
                    theme_text_color="Hint"
                ))
                return

            sorted_items = []
            for item_id, item_data in menu_items.items():
                item_data['id'] = item_id
                sorted_items.append(item_data)

            sorted_items.sort(key=lambda x: (x.get('category', 'z'), x.get('name', '')))

            current_category = None

            for item_data in sorted_items:
                category = item_data.get('category')
                if category and category != current_category:
                    current_category = category
                    self.ids.menu_list.add_widget(MDLabel(
                        text=category.upper(),
                        font_style="H6",
                        halign="left",
                        bold=True,
                        theme_text_color="Primary",
                        size_hint_y=None,
                        height=dp(40),
                        padding=[dp(10), 0]
                    ))

                item_id = item_data['id']
                name = item_data.get('name', 'Unknown Item')
                price = item_data.get('price', 0)
                description = item_data.get('description', '')

                card = MenuItem(
                    name=name,
                    price=price,
                    description=description,
                    item_id=item_id
                )

                card.add_widget(MDLabel(
                    text=name,
                    font_style="H5",
                    theme_text_color="Primary",
                    bold=True,
                    size_hint_y=None,
                    height=dp(40),
                    font_size="22sp"
                ))

                price_label = MDLabel(
                    text=f"₱{price:.2f}",
                    font_style="H6",
                    theme_text_color="Custom",
                    text_color=[0.9, 0.5, 0.1, 1],
                    bold=True,
                    size_hint_y=None,
                    height=dp(30),
                    font_size="20sp"
                )
                card.add_widget(price_label)

                if description:
                    card.add_widget(MDLabel(
                        text=description,
                        font_style="Caption",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(40),
                        font_size="14sp"
                    ))

                button_box = MDBoxLayout(
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(10),
                    padding=[0, dp(5), 0, 0]
                )

                add_button = MDRaisedButton(
                    text="Add to Cart",
                    pos_hint={"center_y": 0.5},
                    on_release=lambda btn, c=card: c.add_to_cart(),
                    md_bg_color=[0.12, 0.65, 0.32, 1]
                )
                button_box.add_widget(add_button)

                card.add_widget(button_box)
                self.ids.menu_list.add_widget(card)

        except Exception as e:
            toast(f"Error loading menu: {str(e)}")
            self.ids.menu_list.clear_widgets()
            self.ids.menu_list.add_widget(MDLabel(
                text=f"Error loading menu. Please try again.",
                halign="center",
                theme_text_color="Error"
            ))

    def navigate_to_cart(self):
        """Navigate to the cart screen"""
        self.manager.transition.direction = 'left'
        self.manager.current = "cart_screen"

    def go_back(self):
        """Return to the dashboard"""
        self.manager.transition.direction = 'right'
        self.manager.current = "user_dashboard"