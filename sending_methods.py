from requests import put, post
from aiokafka import AIOKafkaProducer as Producer
from json import dumps


async def send_stock_kafka(loop, state, data):
    producer = Producer(loop=loop, bootstrap_servers='0.0.0.0:9092')
    print(data['Meta Data']['2. Symbol'])
    await producer.start()
    try:
        await producer.send_and_wait(f"API_Handler_{state}_Out", key={data['Meta Data']['2. Symbol']}, value=data)
    finally:
        await producer.stop()


def send_stock_http(method, data):
    if method == "PUT":
        # what the hell is going in with the comma and symbol i don't know
        response = put(f"http://127.0.0.1:5000/API_Handler,{data['Meta Data']['2. Symbol']}", json=data)
    elif method == "POST":
        response = post("http://127.0.0.1:5000/API_Handler", json=data)
    else:
        raise ValueError("Method mus be PUT or POST")
    handle_db_response(response, data['Meta Data']['2. Symbol'])


def handle_db_response(response, stock_symbol):
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

