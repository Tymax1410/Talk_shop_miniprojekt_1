# =====================================================================================
#                                        INCLUDES
# =====================================================================================
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from sqlalchemy import Float, Integer, String, create_engine, select, Select
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# =====================================================================================
#                                     DATA MODEL
# =====================================================================================
@dataclass
class Product:
    name: str
    price: float
    stock: int


example_data: list[Product] = [
    Product(name="Monorail", price=1449.99, stock=30),
    Product(name="Hewlett Packard", price=1849.99, stock=23),
    Product(name="COMPAQ", price=2399.99, stock=8),
]


# =====================================================================================
#                                    DATABASE INTERFACE
# =====================================================================================
class DatabaseModel(DeclarativeBase):
    pass


class ProductModel(DatabaseModel):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float())
    stock: Mapped[int] = mapped_column(Integer())

    def from_model(self)-> Product:
        return Product(name=self.name, price=self.price, stock=self.stock)

    @staticmethod
    def to_model(product: Product) -> ProductModel:
        return ProductModel(name=product.name, price=product.price, stock=product.stock)


def prepare_db()-> Engine:
    Path("local").mkdir(exist_ok=True)
    engine = create_engine("sqlite:///local/demo.db")
    DatabaseModel.metadata.create_all(engine)
    return engine

def write_to_db(products: list[Product], eng: Engine)-> None:
    with Session(eng) as session:
        for product in products:
            session.add(ProductModel.to_model(product))
        session.commit()

def retrieve_product_by_name(name: str, eng: Engine)-> list[Product]:
    products: list[Product] = []
    with Session(eng) as session:
        query: Select[ProductModel] = select(ProductModel).where(ProductModel.name == name)
        product_models: Sequence[ProductModel] = session.scalars(query).all()
        for product_model in product_models:
            products.append(product_model.from_model())
    return products

def retrieve_all_products(eng: Engine)-> list[Product]:
    products: list[Product] = []
    with Session(eng) as session:
        query: Select[ProductModel] = select(ProductModel)
        product_models: Sequence[ProductModel] = session.scalars(query).all()
        for product_model in product_models:
            products.append(product_model.from_model())
    return products

def delete_product_by_name(name: str, eng: Engine) -> None:
    with Session(eng) as session:
        query: Select[ProductModel] = select(ProductModel).where(ProductModel.name == name)
        product_to_delete = session.scalars(query).first()
        if product_to_delete is not None:
            session.delete(product_to_delete)
        session.commit()

def update_product_by_name(name: str, new_price: float, new_stock: int, eng: Engine) -> None:
    with Session(eng) as session:
        query: Select[ProductModel] = select(ProductModel).where(ProductModel.name == name)
        product_to_update = session.scalars(query).first()
        if product_to_update is not None:
            product_to_update.price = new_price
            product_to_update.stock = new_stock
        session.commit()

def clear_db(eng: Engine)-> None:
    with Session(eng) as session:
        session.query(ProductModel).delete(synchronize_session="fetch")
        session.commit()

def add_product(eng:Engine):
    while True:
        name_of_product = input("Input name of the product > ")
        try:
            price_of_product = float(input("Input price of the product > "))
        except ValueError:
            print("This is not correct format of price (ex: 14.99)")
            continue
        try:
            stock_of_product = int(input("Input stock of the product > "))
        except ValueError:
            print("This is not correct format of stock (ex: 5)")
            continue
        new_product = Product(name_of_product, price_of_product, stock_of_product)
        write_to_db([new_product],eng)
        question = input("If you want to add another product, type Y. > ").upper()
        if question == "Y":
            continue
        else:
            break

def search_product(eng: Engine):
    while True:
        name_of_product = input("Input name of the product > ")
        product = retrieve_product_by_name(name_of_product, eng)
        if not product:
            print("This product is not in this database")
        else:
            print(product)
        question = input("If you want to search for another product, type Y. > ").upper()
        if question == "Y":
            continue
        else:
            break

def show_all_products(eng: Engine):
    products = retrieve_all_products(eng)
    if not products:
        print("Database is empty")
    for product in products:
        print(product)

def delete_product(eng: Engine):
    while True:
        name_of_product = input("Input name of the product > ")
        product = retrieve_product_by_name(name_of_product, eng)
        if not product:
            print("This product is not in this database")
        else:
            question = input(f"If you sure you want delete {name_of_product}, type Y . > ").upper()
            if question == "Y":
                delete_product_by_name(name_of_product,eng)
                print("Success")
        question = input("If you want to delete another product, type Y . > ").upper()
        if question == "Y":
            continue
        else:
            break

def edit_product(eng: Engine):
    while True:
        name_of_product = input("Input name of the product > ")
        product = retrieve_product_by_name(name_of_product, eng)
        if not product:
            print("This product is not in this database")
        else:
            try:
                new_price= float(input("Input new price of the product > "))
            except ValueError:
                print("This is not correct format of price (ex: 14.99)")
                continue
            try:
                new_stock = int(input("Input new stock of the product > "))
            except ValueError:
                print("This is not correct format of stock (ex: 5)")
                continue
            update_product_by_name(name_of_product, new_price, new_stock, eng)
            print("Success")
        question = input("If you want to edit another product, type Y. > ").upper()
        if question == "Y":
            continue
        else:
            break

def clear_database(eng: Engine):
    question = input("If you sure you want to delete database, type Y .").upper()
    if question == "Y":
        clear_db(eng)
        print("Success")

def admin_menu(eng: Engine):
    while True:
        choice = input("""
Choose your option (input number only from 0-6):
1. Add product
2. Search for the product by name
3. Edit product by name
4. Delete product by name
5. Show all products
6. Clear database
0. Exit
> """)
        if choice == "1":
            add_product(eng)
        elif choice == "2":
            search_product(eng)
        elif choice == "3":
            edit_product(eng)
        elif choice == "4":
            delete_product(eng)
        elif choice == "5":
            show_all_products(eng)
        elif choice == "6":
            clear_database(eng)
        elif choice == "0":
            break
        else:
            print(f"There is no option like this '{choice}' in menu")


# =====================================================================================
#                                    MAIN
# =====================================================================================
def main()-> None:
    eng = prepare_db()
    clear_db(eng)
    write_to_db(example_data, eng)
    products = retrieve_product_by_name("Monorail", eng)
    for product in products:
        print(product)

if __name__ == "__main__":
    main()