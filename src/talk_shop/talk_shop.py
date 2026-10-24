# =====================================================================================
#                                     IMPORTS
# =====================================================================================
from lark import Lark, Token, Tree
from lark.exceptions import LarkError
from dataclasses import dataclass
import argparse
import logging

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
        logging.error(f"I couldn't find this product in this query:{query}")
        return "This product is currently unavailable."
    except LarkError:
        logging.error(f"Check if we can expand this LLM for this question/option:{query}")
        return"I don't understand your question."

# =====================================================================================
#                                       LOGGING
# =====================================================================================

def setup_logging(log_file: str, log_level: str):
    logging.basicConfig(
        filename = log_file,
        level = log_level.upper(),
        format = "%(asctime)s - %(levelname)s - %(message)s"
        )

# =====================================================================================
#                           OBSŁUGA ARGUMENTÓW COMMAND LINE'A
# =====================================================================================
def parse_args():
    parser = argparse.ArgumentParser(description="Talk Shop - shopping assistant")
    parser.add_argument(
        "-g","--grammar",
        type=str,
        required=True,
        help="Path to the file with grammar"
    )
    parser.add_argument(
        "-lf","--log-file",
        default="app.log",
        type=str,
        help="Path to the file with logs"
    )
    parser.add_argument(
        "-ll","--log-level",
        default="INFO",
        type=str,
        help="Log level info"
    )
    return parser.parse_args()

def load_grammar(grammar_path: str):
    with open(grammar_path,"r", encoding="utf-8") as file:
        grammar_text = file.read()
    return grammar_text
# =====================================================================================
#                                        MAIN
# =====================================================================================
def main()->None:
    args = parse_args()
    setup_logging(args.log_file, args.log_level)
    grammar_text = load_grammar(args.grammar)
    parser = Lark(grammar_text, parser="earley")
    while True:
        query = input("Query > ")
        if query == "END":
            break
        response = process_query(query, parser)
        print(response)


if __name__ == "__main__":
    main()