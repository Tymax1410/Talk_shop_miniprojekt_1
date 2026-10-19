# =====================================================================================
#                                     IMPORTS
# =====================================================================================
from lark import Lark, Token, Tree
from dataclasses import dataclass

# ======================================================================================
#                                     DATA MODEL
# ======================================================================================
@dataclass
class Product:
    name: str
    price: float
    stock: int


products: dict[str, Product] = {
    "monorail": Product(name="Monorail", price=1449.99, stock=30),
    "hewlett_packard": Product(name="Hewlett Packard", price=1849.99, stock=23),
    "compaq": Product(name="COMPAQ", price=2399.99, stock=8),
}

# =====================================================================================
#                                      NLP
# =====================================================================================

#
# How much is the jacket
#
#

grammar = """
%import common.WS
%ignore WS

start: price_question

price_question: HOW_MUCH BE DET ITEM | HOW_MUCH BE ITEM

HOW_MUCH : "how much"
BE : "is"|"are"
DET : "the"|"a"|"any"
ITEM : /[a-z]+/
"""

def pretty_print(node: Tree|Token, depth: int=0)->None:
    if isinstance(node, Token):
        print("  "*depth + f"{node.type} = {node}")
        return
    print("  "*depth + node.data)
    for subtree in node.children:
        pretty_print(subtree, depth+1)
    

def process_query(query: str)-> str:
    parser = Lark(grammar, parser="earley")
    tree = parser.parse(query)
    query_node: Tree | Token = tree.children[0]
    if isinstance(query_node, Token):
        return "Unable to process query."
    if query_node.data == "price_question":
        item = list(query_node.find_token("ITEM"))[0]
        if not isinstance(item, Token):
            return "Unable to process query."
        return f"The {item} costs {products[str(item)].price}$"

# =====================================================================================
#                                        MAIN
# =====================================================================================
def main()->None:
    response = process_query(input("Query : "))
    print(response)

if __name__ == "__main__":
    main()