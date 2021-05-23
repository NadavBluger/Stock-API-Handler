import time
from stockrequests import TimeSeriesDailyRequest
from requests import put, get, post
from json import dumps


req1 = TimeSeriesDailyRequest(outputsize="full")


def get_stock_symbols():
    """
    Aquires all stock symbols from the API
    :return: A list of all symbols
    """
    stocks_data = get("https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=0MM5MCP66HZMFZ8H").text
    rows = stocks_data.split("\r\n")
    rows.pop(0)
    rows.pop()
    stock_symbols = []
    for row in rows:
        stock_symbols.append(row.split(",")[0])
    print(len(stock_symbols))
    return stock_symbols


def save_response_to_file(response, symbol):
    with open(".\\Bad Requests\\{}.json".format(symbol), mode='w') as f:
        f.write(dumps(response))


def loop_through_stocks(method):
    symbols = get_stock_symbols()
    time.sleep(12.001)  # the Api key is limited to 5 requests per minute
    for stock_symbol in symbols:
        start_time = time.time()
        response = req1.preform_request(stock_symbol)
        if "Meta Data" in response.keys() and "Time Series (Daily)" in response.keys():
            db_response = send_stock(method, response)
            if db_response.status_code != 200:
                print("DB operation was not successful")
                save_response_to_file(response, stock_symbol)
                # Implement a logger here
        else:
            print("Bad response received")
            save_response_to_file(response, stock_symbol)
            # Implement a logger here
        time.sleep(12.001-(time.time()-start_time))  # the Api key is limited to 5 requests per minute


def send_stock(method, data):
    if method == "PUT":
        return put("http://127.0.0.1:5000/API_Handler", json=data)
    elif method == "POST":
        return post("http://127.0.0.1:5000/API_Handler", json=data)
    else:
        raise ValueError("Method mus be PUT or POST")


def main():
    loop_through_stocks("POST")
    while True:
        loop_through_stocks("PUT")


if __name__ == '__main__':
    while True:
        main()




# check differance between data and JSON in PUT and POST methods
