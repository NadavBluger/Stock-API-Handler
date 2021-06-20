import time
import asyncio
from stockrequests import TimeSeriesDailyRequest, ListingStatus
from sending_methods import save_response_to_file
from commons.loggers import TextFileLogger
from commons.configurations import JSONFileConfiguration
from commons.RabbitMQ import RabbitMQAgent
from json import dumps


async def get_stock_symbols(logger):
    """
    Aquires all stock symbols from the API
    :return: A list of all symbols
    """
    logger.log("Acquiring a list of all stock symbols", "DEBUG")
    request = ListingStatus(logger=logger)
    return await request.preform_request()


async def loop_through_stocks(method, agent, logger):
    """
    Loop through a list of tickers, get thier data from the api and send it forward
    :param method: PUT or POST, POST is for the first run when all tickers are first requested
    :param agent: A queue management broker agent tasked with sending the data once retrieved
    :param logger: a logger
    :return:
    """
    symbols = await get_stock_symbols(logger)
    time.sleep(12.001)  # the Api key is limited to 5 requests per minute
    for stock_symbol in symbols:
        start_time = time.time()
        response = await req1.preform_request(stock_symbol)
        if "Meta Data" not in response.keys() or "Time Series (Daily)" not in response.keys():
            save_response_to_file(response, stock_symbol)
            logger.log(f"Bad response was received for {stock_symbol} and was saved to file", "WARN")
            continue
        await asyncio.sleep(12.001 - (time.time() - start_time))  # the Api key is limited to 5 requests per minute
        message = {"method": method, "data": response}
        await agent.write(dumps(message))


async def main(agent, logger):
    await loop_through_stocks("POST", agent, logger)
    while True:
        await loop_through_stocks("PUT", agent, logger)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    rabbit_config = JSONFileConfiguration(["credentials", "host", "output_exchanges", "input_exchanges", "input_queue"],
                                          "./Configurations/RabbitMQConfiguration.json")
    logger_config = JSONFileConfiguration(["level"], "./Configurations/LoggerConfiguration.json")
    rabbit_agent = RabbitMQAgent(rabbit_config, loop)
    logger_args = logger_config.__dict__.copy()
    logger_args.pop("level")
    logger_args.pop("needed_params")
    logger_args.pop("params")
    logger_args.pop("file_path")
    text_logger = TextFileLogger(logger_config.level, **logger_args)
    req1 = TimeSeriesDailyRequest(outputsize="full", logger=text_logger)
    loop.run_until_complete(main(rabbit_agent, text_logger))
