import pprint
import requests

class StockTwitsAPI():

    def __init__(self):
        self.streams_url = "https://api.stocktwits.com/api/2/streams/user/{}.json"
        self.symbols_url = "https://api.stocktwits.com/api/2/symbols/with_price/{}.json?extended=true"
        self.headers = {'accept': 'application/json'}

    def fetch_user_posts(self, user_name:str, since:int=None, max:int=None, messages_count:int=21, media_filter:str="all") -> dict:
        """
        Retrieves a specified number of the most recent posts made by a certain user.
        The user can be identified by either their username or user ID.
        Optional parameters can be used to filter the results by message ID or media type.

        Parameters:
            user_name (str): The username or user ID of the user whose posts are to be retrieved.
            since (int): Only retrieve posts with an ID greater than this value.
            max (int): Only retrieve posts with an ID less than or equal to this value.
            messages_count (int): The number of posts to retrieve, defaults to 30.
            media_filter (str): Only retrieve posts containing the specified media type.

        Returns:
            dict: JSON representation of the retrieved posts.
        """
        url = self.streams_url.format(user_name)
        
        params = {
            'since': since,
            'max': max,
            'limit': messages_count,
            'filter': media_filter
        }
        params = {k: v for k, v in params.items() if v is not None}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print("Something went wrong:",err)

    def fetch_symbol_price(self,symbol: str):
        """
        Get the price of a given symbol
        """
        url = self.symbols_url.format(symbol)
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            price = response.json()['symbol']['price_data']['Last']
            return price
        except requests.exceptions.HTTPError as errh:
            print("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print("Something went wrong:",err)

print(StockTwitsAPI().fetch_symbol_price("AAPL"))