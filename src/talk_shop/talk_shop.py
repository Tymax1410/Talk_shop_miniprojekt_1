# =====================================================================================
#                                     IMPORTS
# =====================================================================================
from lark import Lark, Token, Tree
from lark.exceptions import LarkError
from dataclasses import dataclass
import argparse

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

def pretty_print(node: Tree|Token, depth: int=0)->None:
    if isinstance(node, Token):
        print("  "*depth + f"{node.type} = {node}")
        return
    print("  "*depth + node.data)
    for subtree in node.children:
        pretty_print(subtree, depth+1)
    

def process_query(query: str, parser: Lark)-> str:
    try:
        tree = parser.parse(query)
        query_node: Tree | Token = tree.children[0]
        if isinstance(query_node, Token):
            return "Unable to process query."
        if query_node.data == "price_question":
            item = list(query_node.find_token("ITEM"))[0]
            if not isinstance(item, Token):
                return "Unable to process query."
            return f"The {item} costs {products[str(item)].price}$"
        if query_node.data == "stock_question":
            item = list(query_node.find_token("ITEM"))[0]
            if not isinstance(item, Token):
                return "Unable to process query."
            return f"The  quantity of {item} is {products[str(item)].stock}"
        return "Unable to process query."
    except KeyError:
        return "This product is currently unavailable"
    except LarkError:
        return"I don't understand your question"


# =====================================================================================
#                           OBSŁUGA ARGUMENTÓW COMMAND LINE'A
# =====================================================================================
def parse_args():
    parser = argparse.ArgumentParser(description="Talk Shop - shopping assistant")
    parser.add_argument(
        "-g","--grammar",
        type=str,
        required=True,
        help="Ścieżka do pliku z gramatyką"
    )
    return parser.parse_args()

def load_grammar():
    args = parse_args()
    with open(args.grammar, "r", encoding="utf-8") as file:
        grammar_text = file.read()
    return grammar_text
# =====================================================================================
#                                        MAIN
# =====================================================================================
def main()->None:
    grammar_text = load_grammar()
    parser = Lark(grammar_text, parser="earley")
    while True:
        query = input("Query > ")
        if query == "END":
            break
        response = process_query(query, parser)
        print(response)


if __name__ == "__main__":
    main()