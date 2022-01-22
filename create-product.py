from ast import While
from urllib import parse
import json
import requests
import sys
import re
import base64

GROCY_URL = "https://link.to.grocy/api/"
DEFAULT_GROUP = "8"
DEFAULT_LOCATION = "3"


def get_barcode() -> str:
    while(True):
        barcode = input("Barcode: ").strip()
        if barcode == "":
            sys.exit(0)
        # Check if barcode exist in grocy
        bc_exist = requests.get(
            GROCY_URL + "stock/products/by-barcode/" + barcode)
        if bc_exist.status_code == 400:
            return barcode
            break
        else:
            existing_product = json.loads(bc_exist.content)
            print("Barcode already exists in Grocy for product",
                  existing_product["product"]["name"], "with id", existing_product["product"]["id"])


def get_quantities(qu_str):
    qu_name = ""
    qu_value = ""

    if (match := re.search("([a-zA-Z]+)", qu_str)) is not None:
        qu_name = match.group(0)
    if (match := re.search("([\d,\.]+)", qu_str)) is not None:
        qu_value = match.group(0)

    qu_id = ""
    for id in quantities:
        if quantities[id].casefold() == qu_name.casefold():
            qu_id = id
    return qu_value, qu_id


def set_product_name(default_product_name) -> None:
    while(True):
        new_product["name"] = input(
            "Product name ["+default_product_name+"]: ") or default_product_name
        if not new_product["name"]:
            exit(0)
        query = parse.quote_plus("query[]") + "=name=" + \
            parse.quote_plus(new_product["name"])

        product_exist = requests.get(
            GROCY_URL + "objects/products?" + query)
        if product_exist.status_code == 200:
            existing_product = json.loads(product_exist.content)
            if len(existing_product) == 0:
                break
            print("Product already exists in Grocy",
                  existing_product[0]["name"], "with id", existing_product[0]["id"])
        else:
            break


def add_picture_to_product(id, file_url) -> None:
    response = requests.get(file_url)
    image_name64 = base64.b64encode((str(id) + ".jpg").encode("utf-8"))
    image_name = str(image_name64, "utf-8")
    req = requests.put(
        GROCY_URL + 'files/productpictures/' + image_name, data=response.content)
    if(req.status_code < 400):
        req = requests.put(GROCY_URL + 'objects/products/' +
                           str(id), data={"picture_file_name": str(id) + ".jpg"})


def add_calories(productData) -> None:
    cal = int(productData["product"]["nutriments"]["energy-kcal_100g"])
    new_cal = 0
    if (quantities[new_product["qu_id_stock"]].lower() == "g" or quantities[new_product["qu_id_stock"]].lower() == "ml"):
        new_cal = str(cal / 100.0)
    if (quantities[new_product["qu_id_stock"]].lower() == "kg" or quantities[new_product["qu_id_stock"]].lower() == "l"):
        new_cal = str(cal / 1000.0)
    new_product["calories"] = new_cal


def add_product_group() -> None:
    print("Available product groups:")
    for id in groups:
        print(id, "=", groups[id], ", ", end='')
    print("")
    prompt = "Default group"
    if DEFAULT_GROUP:
        prompt = prompt + " [" + groups[DEFAULT_GROUP] + "]"
    group_id = product_group = input(prompt + ": ") or DEFAULT_GROUP
    if not group_id:
        sys.exit(2)
    new_product["product_group_id"] = group_id


def add_location() -> None:
    new_product["location_id"] = DEFAULT_LOCATION
    if not new_product["location_id"]:
        print("\nAvailable locations:")
        for id in locations:
            print(id, "=", locations[id], ", ", end='')
        print("")
        new_product["location_id"] = input(
            "Default location [" + list(locations.keys())[0] + "]: ") or list(locations.keys())[0]
    else:
        print("Default location: ",
              locations[DEFAULT_LOCATION], " [", DEFAULT_LOCATION, "]")


def add_quantities(productData) -> None:
    qu_f = ""
    qu_id = ""
    qu_value = ""

    if "quantity" in productData["product"]:
        qu_f = productData["product"]["quantity"]
        result = get_quantities(qu_f)
        qu_value = result[0]
        qu_id = result[1]

    if not qu_id or not qu_value:
        qu_f = input(
            "Enter quantity and unit of scanned barcode product (e.g. 1000g): ") or ""
        if not qu_f:
            sys.exit(2)
        result = get_quantities(qu_f)
        qu_value = result[0]
        qu_id = result[1]
    else:
        confirm = input(
            "Confirm quantity and unit of scanned barcode product with ENTER or enter new value [" + qu_value + " " + quantities[qu_id] + " (" + qu_id + ")]: ") or "ok"
        if not confirm == "ok":
            result = get_quantities(confirm)
            qu_value = result[0]
            qu_id = result[1]

    new_barcode["qu_id"] = qu_id
    new_barcode["amount"] = qu_value
    new_product["qu_id_stock"] = qu_id
    new_product["qu_factor_purchase_to_stock"] = qu_value

    print("Available quantities:")
    for id in quantities:
        print(id, "=", quantities[id], ", ", end='')
    print("")
    qu_f = input(
        "Enter purchase quantity unit [" + quantities[qu_id] + "]: ") or quantities[qu_id]
    result = get_quantities(qu_f)
    new_product["qu_id_purchase"] = result[1]


def load_grocy_data():
    locations_json = requests.get(GROCY_URL + "objects/locations")
    if locations_json.status_code < 400:
        locations_parsed = json.loads(locations_json.content)
        for location in locations_parsed:
            locations[location["id"]] = location["name"]

    qu_json = requests.get(GROCY_URL + "objects/quantity_units")
    if qu_json.status_code < 400:
        qu_parsed = json.loads(qu_json.content)
        for qu in qu_parsed:
            quantities[qu["id"]] = qu["name"]

    groups_json = requests.get(GROCY_URL + "objects/product_groups")
    if groups_json.status_code < 400:
        groups_parsed = json.loads(groups_json.content)
        for group in groups_parsed:
            groups[group["id"]] = group["name"]


def create_new_product():
    new_barcode["barcode"] = get_barcode()

    off_response = requests.get(
        "https://de.openfoodfacts.org/api/v0/product/" + new_barcode["barcode"] + ".json")
    if off_response.status_code >= 400:
        sys.exit(1)
    product = json.loads(off_response.content)
    def_product = ""
    if product["status"] == 0:
        obf_response = requests.get(
            "https://de.openbeautyfacts.org/api/v0/product/" + new_barcode["barcode"] + ".json")
        product = json.loads(obf_response.content)
        if obf_response.status_code >= 400:
            sys.exit(1)
        if product["status"] != 0:
            if "product_name" in product["product"]:
                def_product = product["product"]["product_name"]
    else:
        if "product_name" in product["product"]:
            def_product = product["product"]["product_name"]
        if "product_name_de" in product["product"]:
            def_product = product["product"]["product_name_de"]

    set_product_name(def_product)

    add_quantities(product)

    add_location()

    add_product_group()

    if('energy-kcal_100g' in product['product']['nutriments'] and product['product']['nutriments']['energy-kcal_100g']):
        add_calories(product)

    create_response = requests.post(
        GROCY_URL + "objects/products", data=new_product)
    if create_response.status_code >= 400:
        print("Error creating product in Grocy: ",
              create_response.status_code, ": ", create_response.content)
        sys.exit(3)
    new_product_id = json.loads(create_response.content)["created_object_id"]

    new_barcode["product_id"] = new_product_id
    create_response = requests.post(
        GROCY_URL + "objects/product_barcodes", data=new_barcode)
    if create_response.status_code >= 400:
        print("Error creating barcode in Grocy: ",
              create_response.status_code, ": ", create_response.content)
        sys.exit(3)
    print("New product created with id: ", new_product_id)

    # Add image
    if("image_url" in product["product"] and product["product"]["image_url"]):
        add_picture_to_product(new_product_id, product["product"]["image_url"])


locations = {}
quantities = {}
groups = {}

new_product = {}
new_barcode = {}

load_grocy_data()

# Main loop to create new products
while(True):
    create_new_product()
