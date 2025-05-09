from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SwapTransition
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.user_dashboard import UserDashboard
from screens.menu_screen import MenuScreen
from screens.cart_screen import CartScreen
from screens.checkout_screen import CheckoutScreen
from screens.order_confirmation import OrderConfirmScreen
from screens.admin_dashboard import AdminDashboard
from screens.orders_screen import Orders
from screens.menu_management_screen import MenuManagement

class GrabPiyudApp(MDApp):
    cart = {}

    def build(self):
        self.icon = "assets/GrabPiyud_gbg256circle.png"
        self.title = "Grab Piyu-d"
        self.theme_cls.primary_palette = "Green"

        Builder.load_file("kv/login_screen.kv")
        Builder.load_file("kv/register_screen.kv")
        Builder.load_file("kv/user_dashboard.kv")
        Builder.load_file("kv/menu_screen.kv")
        Builder.load_file("kv/cart_screen.kv")
        Builder.load_file("kv/checkout_screen.kv")
        Builder.load_file("kv/order_confirmation.kv")
        Builder.load_file("kv/admin_dashboard.kv")
        Builder.load_file("kv/orders_screen.kv")
        Builder.load_file("kv/menu_management_screen.kv")


        sm = ScreenManager(transition=SwapTransition())

        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(RegisterScreen(name="register_screen"))

        sm.add_widget(UserDashboard(name="user_dashboard"))
        sm.add_widget(MenuScreen(name="menu_screen"))
        sm.add_widget(CartScreen(name="cart_screen"))
        sm.add_widget(CheckoutScreen(name="checkout_screen"))
        sm.add_widget(OrderConfirmScreen(name="order_confirmation"))

        sm.add_widget(AdminDashboard(name="admin_dashboard"))
        sm.add_widget(MenuManagement(name="menu_management_screen"))
        sm.add_widget(Orders(name="orders_screen"))

        # sm.current = "admin_dashboard"

        return sm

    def logout(self):
        self.root.current = "login_screen"

GrabPiyudApp().run()
