from fastapi import FastAPI
from controllers.product_controller import list_products
from controllers.cart_controller import view_cart, add_to_cart
from controllers.checkout_controller import process_checkout

app = FastAPI()

@app.get("/products")
def products():
    return list_products()

@app.get("/cart")
def cart():
    return view_cart()

@app.post("/cart/add")
def cart_add():
    return add_to_cart()

@app.post("/checkout")
def checkout():
    return process_checkout()
