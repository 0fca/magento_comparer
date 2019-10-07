import json
import logging
import sys

from serializer import Serializer
from rest_client import RestClient


def get_special_price_attr(attribute_list, attr_name):
    for attr in attribute_list:
        if attr["attribute_code"] == attr_name:
            return attr


def get_product_list(headers):
    rest_client = RestClient()
    products = rest_client.send_get(
        "http://" + sys.argv[1] + "/rest/default/V1/products?searchCriteria[filter_groups][0][filters][0][field]=sku&"
                                  "searchCriteria[filter_groups][0][filters][0][condition_type]=notnull",
        headers, None)
    return products


def authorize_user(rest_client):
    user = {
        "username": sys.argv[3],
        "password": sys.argv[4]
    }

    response = rest_client.send_post("http://" + sys.argv[1] + "/rest/V1/integration/admin/token",
                                     {"Content-Type": "application/json"},
                                     json.dumps(user)
                                     )

    if response[1] != 200:
        logging.error("Error authorizing user.")

    return response[0]


def prepare_different_items_list(rest_client, headers):
    serializer = Serializer()
    xml = rest_client.send_get_binary(sys.argv[5], None, None)
    root_item = serializer.deserialize_xml(str(xml[0], "utf8"))
    commodities = root_item

    read_item_list = list()

    magento_product_list = list(get_product_list(headers)[0]["items"])

    magento_product_dict = dict()

    for magento_product in magento_product_list:
        magento_product_dict[magento_product["sku"]] = magento_product

    for commodity in commodities:
        if commodity[1].text in magento_product_dict:
            magento_product = magento_product_dict[commodity[1].text]
            sku = commodity[1].text
            price = float(commodity[3][0].text)
            special_price = float(commodity[3][1].text)

            read_item = {
                "product": {
                    "sku": sku,
                    "price": price,
                    "name": sku,
                    "type_id": magento_product["type_id"],
                    "attribute_set_id": magento_product["attribute_set_id"],
                    "custom_attributes": {
                        "special_price": special_price
                    }
                }
            }

            price = float(magento_product["price"])
            attribute = get_special_price_attr(magento_product["custom_attributes"], "special_price")
            special_price = float(attribute["value"])

            if price != float(commodity[3][0].text) or special_price != float(commodity[3][1].text):
                read_item_list.append(read_item)
        else:
            logging.error("There is not product of sku {0} in Magento database.".format(commodity[1].text))

    return read_item_list


def update_magento_products(rest_client, headers, read_item_list):
    logging.info("Starting update products procedure.")
    if len(read_item_list) > 0:
        for product in read_item_list:
            if product:
                json_content = json.dumps(product)
                magento_product = \
                    rest_client.send_get("http://" + sys.argv[1] + "/rest/V1/products/" + product["product"]["sku"],
                                         headers, None)[0]

                attribute = get_special_price_attr(magento_product["custom_attributes"], "special_price")

                logging.info(
                    "Processing product: {0}, changing old values [{1},{2}] to the following: price = {3}, "
                    "special price = {4} "
                    .format(product['product']['sku'],
                            magento_product["price"],
                            attribute["value"],
                            product['product']['price'],
                            product['product']['custom_attributes']['special_price']))

                response = rest_client.send_put(
                    "http://" + sys.argv[1] + "/rest/V1/products/" + product['product']['sku'],
                    headers,
                    json_content
                )

                if response[1] == 200:
                    logging.info("Successfully updated product.")
                else:
                    logging.error("Server answered with {0} code, message: {1}".format(response[1], response[0]))
    else:
        logging.info("No different products found between xml file and magento db.")

    logging.info("Update products procedure ended.")


def add_dummy_products(rest_client, headers):
    serializer = Serializer()
    xml = rest_client.send_get_binary(sys.argv[5], None, None)
    root_item = serializer.deserialize_xml(str(xml[0], "utf8"))
    commodities = root_item

    read_item_list = list()

    for item in commodities:
        read_item = {
            "product": {
                "sku": item[1].text,
                "price": 0,
                "name": item[1].text,
                "status": 1,
                "visibility": 4,
                "type_id": "simple",
                "attribute_set_id": 4,
                "custom_attributes": {
                    "special_price": 0
                }
            }
        }
        read_item_list.append(read_item)

    if read_item_list:
        json_content = json.dumps(read_item_list)
        json_data = rest_client.send_post("http://" + sys.argv[1] + "/rest/V1/products/",
                                          headers,
                                          json_content
                                          )
        if json_data[1] != 200:
            logging.error(json_data[0]["message"])


def main():
    print("Logging to file " + sys.argv[2] + 'magento_updater.log')
    logging.basicConfig(filename=sys.argv[2] + 'magento_updater.log', filemode='a',
                        format='%(asctime)s - %(message)s', level=logging.INFO)

    mode = "prod"

    if sys.argv[6] is not None:
        mode = sys.argv[6]

    rest_client = RestClient()

    token = authorize_user(rest_client)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }
    if mode == "devel":
        add_dummy_products(rest_client, headers)

    logging.info("User has been successfully logged in.")

    read_item_list = prepare_different_items_list(rest_client, headers)

    update_magento_products(rest_client, headers, read_item_list)

    logging.info("Job done, exiting. Goodbye.")


if __name__ == '__main__':
    main()
