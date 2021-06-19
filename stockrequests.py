from operator import concat
from requests import get
from json import loads


class StockRequest:
    _permitted_arg = []  # implement
    apikey = '0MM5MCP66HZMFZ8H'  # implement

    def __init__(self, function, symbol=None, *, logger, **request_arguments):
        self.logger = logger
        self.symbol = symbol
        self.function = function
        self.arguments = request_arguments
        self.apikey = StockRequest.apikey
        if request_arguments.keys() and request_arguments.keys() not in self._permitted_arg:
            wrong_arg = [k for k in request_arguments.keys() if k not in self._permitted_arg]
            self.logger.log(f"Arguments ({wrong_arg}) which do not fit requests type were given and will not be used",
                            "WARN")

    @property
    def request_url(self):
        """
        A getter for the api request url
        :return: request url
        """
        arguments = list("&{}={}".format(key, value) for key, value in self.arguments.items()
                         if key in self._permitted_arg)
        return ''.join(concat(["https://www.alphavantage.co/query?", "function={}".format(self.function),
                               "&symbol={}".format(self.symbol), "&apikey={}".format(self.apikey)], arguments))

    def preform_request(self, symbol=None):
        """
        preforms a http request to the API 
        :param symbol: the stock symbol
        :return: A dict containing info returned from the api for the stock
        """
        self.symbol = symbol or self.symbol
        if self.symbol:
            return loads(get(self.request_url).text)
        else:
            raise AttributeError("A request can not be preformed without a specification of a symbol", "ERROR")

    def __repr__(self):
        request_arguments = [k + ":" + v for k, v in self.arguments.items()]
        return f"{self.symbol}, {self.function}, {request_arguments}"


class TimeSeriesDailyRequest(StockRequest):
    _permitted_arg = ["adjusted", "outputsize", "datatype"]

    def __init__(self, symbol=None, function="TIME_SERIES_DAILY", *, logger,  **kwargs):
        super().__init__(function, symbol, logger=logger, **kwargs)


class TimeSeriesInterdayExtended(StockRequest):
    _permitted_arg = ["adjusted", "slice", "interval"]

    def __init__(self, slice_="year1month1", interval="60min",
                 symbol=None, function="TIME_SERIES_INTRADAY_EXTENDED", *, logger, **kwargs):
        kwargs["slice"] = slice_
        kwargs["interval"] = interval
        super().__init__(function, symbol, logger=logger, **kwargs)

    @staticmethod
    def slices_generator():
        for year in range(2):
            for month in range(12):
                yield "year{}month{}".format(year + 1, month + 1)

    def process_scv_response(self, data):
        rows = data.split("\r\n")
        cells = {}
        rows.pop(0)
        rows.pop()
        cells["Time Series ({})".format(self.arguments["interval"])] = {}
        for row in rows:
            row_values = row.split(",")
            cells["Time Series ({})".format(self.arguments["interval"])][row_values[0]] = {
                "1. open": row_values[1],
                "2. high": row_values[2],
                "3. low": row_values[3],
                "4. close": row_values[4],
                "5. volume": row_values[5]
            }
        cells["Meta Data"] = {"1.Symbol": self.symbol}
        return cells

    def get_all_slices(self):
        for slice_ in self.slices_generator():
            self.arguments["slice"] = slice_
            yield self.preform_request()

    def preform_request(self, symbol=None):
        """
        preforms a http request to the API
        :param symbol: the stock symbol
        :return: A dict containing info returned from the api for the stock
        """
        self.symbol = symbol or self.symbol
        if self.symbol:
            return self.process_scv_response(get(self.request_url).text)
        else:
            raise AttributeError("A request can not be preformed without a specification of a symbol")


class ListingStatus(StockRequest):
    _permitted_arg = []

    def __init__(self, *, logger):
        super(ListingStatus, self).__init__(function="LISTING_STATUS", logger=logger)

    @staticmethod
    def parse_response(stocks_data):
        """
        Parse the cvs file acquired by the request into a list of tickers
        :param stocks_data: a list of all stock tickers
        :return:
        """
        rows = stocks_data.split("\r\n")
        rows.pop(0)
        rows.pop()
        stock_symbols = []
        for row in rows:
            stock_symbols.append(row.split(",")[0])
        return stock_symbols

    def preform_request(self, symbol=None):
        return self.parse_response(get(self.request_url).text)


if __name__ == '__main__':
    pass
