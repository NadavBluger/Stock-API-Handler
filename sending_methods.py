from requests import put, post
from json import dumps


def send_stock_http(method, data):
    """
    Send the document gotten from the API to the Databse writer via HTTP
    --Function no longer in use
    :param method: The method which to use while sending
    :param data: the api response to be sent
    :return:
    """
    if method == "PUT":
        response = put(f"http://127.0.0.1:5000/API_Handler/,{data['Meta Data']['2. Symbol']}", json=data)
    elif method == "POST":
        response = post("http://127.0.0.1:5000/API_Handler", json=data)
    else:
        raise ValueError("Method mus be PUT or POST")
    handle_db_response(response, data['Meta Data']['2. Symbol'])


def handle_db_response(response, stock_symbol):
    """
    Receive response from  the Database Writer and if the operation was not successful write the returned document
    to file
    --Function no longer in use
    :param response: The Http Response from the Database Writer
    :param stock_symbol: The stock's Ticker
    :return:
    """
    if response.status_code != 200:
        print("DB operation was not successful")
        save_response_to_file(response, stock_symbol)


def save_response_to_file(response, symbol):
    """
    Save a requests response to a file named after the ticker
    :param response: actual data to be saved
    :param symbol: the ticker after which the file is to be named
    :return:
    """
    with open(".\\Bad Requests\\{}.json".format(symbol), mode='w') as f:
        f.write(dumps(response))

