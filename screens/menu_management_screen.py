from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.uix.boxlayout import BoxLayout
from firebase_config import db
from kivymd.toast import toast
from kivy.animation import Animation


class MenuManagement(Screen):
    def on_pre_enter(self):
        self.load_menu_items()

    def load_menu_items(self):
        self.ids.menu_list.clear_widgets()
        self.ids.no_items_label.opacity = 0

        menu_data = db.child("menu").get().val()
        if menu_data:
            for key, item in menu_data.items():
                self.create_menu_card(item.get("name", ""), str(item.get("price", "")), key)
        else:
            self.ids.no_items_label.opacity = 1

    def create_menu_card(self, name="", price="", key=None):
        card = MDCard(
            orientation="vertical",
            padding="10dp",
            size_hint_y=None,
            height="190dp",
            radius=[12],
            md_bg_color=(1, 1, 1, 1),
            opacity=0,
            pos_hint={"center_y": 0.3},
            elevation=1
        )

        fields_box = BoxLayout(
            orientation="vertical",
            spacing="10dp",
            size_hint_y=None,
            height="120dp"
        )

        name_field = MDTextField(
            text=name,
            hint_text="Item Name",
            size_hint_x=1,
            helper_text_mode="on_error"
        )

        price_field = MDTextField(
            text=f"{price}" if not str(price).startswith("₱") else str(price),
            hint_text="Price (₱)",
            size_hint_x=1,
            helper_text_mode="on_error",
            input_filter="float"
        )

        delete_button = MDIconButton(
            icon="trash-can-outline",
            pos_hint={"center_x": 0.95},
            theme_text_color="Custom",
            text_color=(1, 0, 0, 1),
            on_release=lambda x: self.delete_card(card)
        )

        fields_box.add_widget(name_field)
        fields_box.add_widget(price_field)

        card.add_widget(fields_box)
        card.add_widget(delete_button)

        card.name_field = name_field
        card.price_field = price_field
        if key:
            card.key = key

        self.ids.menu_list.add_widget(card)

        anim = Animation(opacity=1, pos_hint={"center_y": 0.5}, d=0.3, t="out_cubic")
        anim.start(card)

        self.ids.no_items_label.opacity = 0

    def delete_card(self, card):
        anim = Animation(opacity=0, pos_hint={"center_y": 0.3}, d=0.3, t="out_cubic")
        anim.start(card)

        anim.bind(on_complete=lambda *args: self.remove_widget_after_animation(card))

        if hasattr(card, "key"):
            try:
                db.child("menu").child(card.key).remove()
            except Exception as e:
                toast("Error deleting item")
                print("Delete error:", e)

    def remove_widget_after_animation(self, card):
        self.ids.menu_list.remove_widget(card)

        if not self.ids.menu_list.children:
            self.ids.no_items_label.opacity = 1

    def add_menu_item(self):
        Animation(opacity=0, d=0.3).start(self.ids.no_items_label)
        self.create_menu_card()

    def save_menu(self):
        has_error = False
        menu_data = {}

        for card in reversed(self.ids.menu_list.children):
            name = card.name_field.text.strip()
            price_text = card.price_field.text.replace("₱", "").strip()

            if not name:
                card.name_field.error = True
                card.name_field.helper_text = "Item name is required"
                has_error = True

            try:
                price = float(price_text)
            except ValueError:
                card.price_field.error = True
                card.price_field.helper_text = "Valid price required"
                has_error = True

            if not has_error:
                if hasattr(card, "key"):
                    menu_data[card.key] = {"name": name, "price": price}
                else:
                    menu_data[name] = {"name": name, "price": price}

        if has_error:
            return

        try:
            db.child("menu").set(menu_data)
            toast("Menu saved successfully.")
        except Exception as e:
            toast("Error saving menu.")
            print("Save error:", e)

        self.load_menu_items()
