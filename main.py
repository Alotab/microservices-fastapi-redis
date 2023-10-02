from fastapi import FastAPI, Body, status
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:8000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# microservices: we can also use a different database in addition to this for client order etc
redis = get_redis_connection(
    host="redis-12065.c55.eu-central-1-1.ec2.cloud.redislabs.com",
    port=12065,
    # port=11844,
    password="saI07QYqxJ7inK2GbdWPc6T3TYSsKzWc",
    decode_responses=True
)


class Product(HashModel):
    name: str 
    price: float
    quantity: int

    class Meta:
        database = redis

class ProductModel(BaseModel):
    name: str 
    price: float
    quantity: int



class Order(HashModel):
    product_id: str 
    price: float 
    fee: float 
    total: float 
    quantity: int 
    status: str # pending, completed, refunded


    class Meta:
        database = redis


@app.get("/products")
def all():
    return [ format(pk) for pk in Product.all_pks()]



def format(pk: str):
    product = Product.get(pk)
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }


@app.post("/product/")
async def create(product: ProductModel):
    product_instance = Product(name=product.name, price=product.price, quantity=product.quantity)
    product_instance.save()
    return product_instance


@app.get('/products/item/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)
   