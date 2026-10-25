# =====================================================================================
#                                        INCLUDES
# =====================================================================================
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

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