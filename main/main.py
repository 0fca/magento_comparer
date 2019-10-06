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
        "http://localhost/magento2/rest/default/V1/products?searchCriteria[filter_groups][0][filters][0][field]=sku&"
        "searchCriteria[filter_groups][0][filters][0][condition_type]=notnull",
        headers, None)
    return products


def authorize_user(rest_client):
    user = {
        "username": sys.argv[2],
        "password": sys.argv[3]
    }

    response = rest_client.send_post("http://localhost/magento2/rest/V1/integration/admin/token",
                                     {"Content-Type": "application/json"},
                                     json.dumps(user)
                                     )

    if response[1] != 200:
        logging.error("Error authorizing user.")

    return response[0]


def preapre_different_items_list(rest_client, headers):
    serializer = Serializer()
    xml = rest_client.send_get_binary(sys.argv[4], None, None)
    root_item = serializer.deserialize_xml(str(xml[0], "utf8"))
    commodities = root_item

    read_item_list = list()

    magento_product_list = list(get_product_list(headers)[0]["items"])

    for commodity in commodities:
        read_item = {
            "product": {
                "sku": commodity[1].text,
                "price": float(commodity[3][0].text),
                "name": commodity[1].text,
                "status": 1,
                "visibility": 4,
                "type_id": "simple",
                "attribute_set_id": 4,
                "custom_attributes": {
                    "special_price": float(commodity[3][1].text)
                }
            }
        }

        for magento_product in magento_product_list:
            if magento_product["sku"] == commodity[1].text:
                price = float(magento_product["price"])
                attribute = get_special_price_attr(magento_product["custom_attributes"], "special_price")
                special_price = float(attribute["value"])

                if price != float(commodity[3][0].text) or special_price != float(commodity[3][1].text):
                    read_item_list.append(read_item)

    return  read_item_list


def update_magento_products(rest_client, headers, read_item_list):
    for product in read_item_list:
        if product:
            json_content = json.dumps(product)
            magento_product = \
                rest_client.send_get("http://localhost/magento2/rest/V1/products/" + product['product']["sku"],
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
                "http://localhost/magento2/rest/V1/products/" + product['product']['sku'],
                headers,
                json_content
            )

            if response[1] == 200:
                logging.info("Successfully updated product.")
            else:
                logging.error("Server answered with {0} code, message: {1}".format(response[1], response[0]))


def main():
    print("Logging to file " + sys.argv[1] + 'magento_updater.log')
    logging.basicConfig(filename=sys.argv[1] + 'magento_updater.log', filemode='a',
                        format='%(asctime)s - %(message)s', level=logging.NOTSET)

    rest_client = RestClient()
    token = authorize_user(rest_client)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }

    logging.info("User has been successfully logged in.")

    read_item_list = preapre_different_items_list(rest_client, headers)

    update_magento_products(rest_client, headers, read_item_list)

    logging.info("Job done, exiting. Goodbye.")


if __name__ == '__main__':
    main()
