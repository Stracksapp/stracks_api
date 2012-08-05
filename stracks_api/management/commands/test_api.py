from django.core.management.base import BaseCommand

from stracks_api import api, levels

class Command(BaseCommand):
    def handle(self, *args, **options):
        token = "vioVk-dtwXK-bCFCl-mshBh"
        a = api.API(api.HTTPConnector("http://localhost:8000/api/v0/log/%s" % token))
        s = a.session()
        r1 = s.request("1.2.3.4", "api test client", "/test")
        r1.log("Hello World 1")
        r1.log("Hello World 2")
        r1.end()

        user = api.Entity(8)
        cart = api.Entity(10)
        order = api.Action(8)

        r2 = s.request("1.2.3.4", "api test client", "/complex")
        r2.log("User ? on cart item ? doing some action",
               level=levels.INFO,
               entities=(user(123, "Woody Woodpecker"),
                         cart(123, "Apple Macbook")),
               tags=("test", "api", "user", "cart"),
               action=order())
        r2.log("User ? eating cart item ?",
               level=levels.DEBUG,
               entities=(user(124, "Buggs Bunny"),
                         cart(124, "Candy bar")),
               tags=("test", "api", "user", "cart"),
               action=order())
        r2.end()
        s.end()

