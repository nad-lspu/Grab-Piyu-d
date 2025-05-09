import json
from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from firebase_config import auth, db
from kivymd.toast import toast

class RegisterScreen(Screen):
    def on_pre_enter(self):
        self.create_role_menu()

    def create_role_menu(self):
        self.role_menu = MDDropdownMenu(
            caller=self.ids.reg_role,
            items=[
                {"text": "User", "on_release": lambda x="User": self.set_role(x)},
                {"text": "Admin", "on_release": lambda x="Admin": self.set_role(x)},
            ],
            width_mult=3,
            max_height=dp(112),
            position = "auto"
        )

    def open_role_menu(self):
        if not hasattr(self, 'role_menu'):
            self.create_role_menu()
        self.role_menu.open()

    def set_role(self, role):
        self.ids.reg_role.text = role
        self.role_menu.dismiss()

    def register_user(self):
        name = self.ids.reg_name
        role = self.ids.reg_role
        email = self.ids.reg_email
        phone = self.ids.reg_phone
        password = self.ids.reg_password

        for field in [name, role, email, password]:
            field.error = False
            field.helper_text = ""
            field.helper_text_mode = "on_error"

        if not name.text:
            name.error = True
            name.helper_text = "Please enter your name"

        if not phone.text or len(phone.text) != 11:
            phone.error = True
            phone.helper_text = "Enter a valid 11-digit number"

        if not role.text:
            role.error = True
            role.helper_text = "Please select a role"

        if not name.text or not role.text:
            return

        if "@" not in email.text or "." not in email.text:
            email.error = True
            email.helper_text = "Invalid email"
            return

        if len(password.text) < 6:
            password.error = True
            password.helper_text = "Must be at least 6 characters"
            return

        if any([field.error for field in [name, phone, role, email, password]]):
            return
        try:
            user = auth.create_user_with_email_and_password(email.text, password.text)
            uid = user['localId']
            id_token = user['idToken']

            db.child("users").child(uid).set({
                "name": name.text,
                "phone": phone.text,
                "role": role.text,
                "email": email.text
            },  user['idToken'])
            toast("Registered successfully!")
            self.manager.current = "login_screen"

            auth.send_email_verification(user['idToken'])
            toast("Verification email sent. Please check your inbox.")

        except Exception as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            print(f"Registration error: {error}")
            toast("Registration failed: " + error.replace("_", " ").capitalize())

    def toggle_password_visibility(self, field):
        field.password = not field.password
        self.ids.show_password_button.text = "[b]Hide Password[/b]" if not field.password else "[b]Show Password[/b]"