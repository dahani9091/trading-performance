from Streamer import StockTwitsAPI
import re
import time
import datetime, pytz, holidays
from reposter import reposter
import config
from sheet_handler import update_sheet

def is_EOD(now = None):
    '''
    Return True if current datetime if End of day 
    '''
    tz = pytz.timezone('US/Eastern')
    us_holidays = holidays.US()

    if not now:
        now = datetime.datetime.now(tz)
        print(now)
        print(datetime.datetime.now())
    openTime = datetime.time(hour = 9, minute = 30, second = 0)
    closeTime = datetime.time(hour = 16, minute = 0, second = 0)
    # If a holiday
    if now.strftime('%Y-%m-%d') in us_holidays:
        return True
    # If before 0930 or after 1600 EST time
    if (now.time() < openTime) or (now.time() > closeTime):
        return True
    # If it's a weekend
    if now.date().weekday() > 4:
        return True

    return False    


def parse_post(client: StockTwitsAPI, post_json: dict):
    try:
        # get post data
        post = post_json.get('messages',[{}])[0]
        post_ticker = post.get('symbols',[{}])[0].get('symbol',None)
        post_body = post.get('body',None)

        # get stock price
        stock_price = client.fetch_symbol_price(post_ticker)

        # get bought price that might be in the text in this format $number.number
        parsed_list = re.findall(r'\$(\d+\.\d+|\d+)', post_body) 
        bought_price = parsed_list[0] if parsed_list else None

        # get Pos which is in a number/number format in that example syntax ¼
        parsed_list = re.findall(r'(\d+\/\d+)', post_body)
        pos = parsed_list[0] if parsed_list else None

        # get trade side
        trade_side = "buy" if "bought" in post_body.lower() else "sell" if "sold" in post_body.lower() else None

        # get timestamp in this format "m/d/y h:m AM or PM" if not EOD else return in this format "m/d/y EOD"
        timestamp = datetime.datetime.now().strftime("%m/%d/%y %I:%M %p") if not is_EOD() else datetime.datetime.now().strftime("%m/%d/%y EOD")
        
        post_data = {
            "body": post_body,
            "timestamp": timestamp,
            "ticker": post_ticker,
            "side": trade_side,
            "price": stock_price,
            "bought_price": bought_price,
            "pos":pos

        }
        return post_data
    except KeyError as e:
        print(f'Error: Missing key in post_json: {e}')
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':

    client = StockTwitsAPI()
    old_post_body:str = None
    print("Waiting for new posts...")
    while True:
        # Pass in all parameters to query search
        post_json = client.fetch_user_posts(user_name=config.stocktwits_username)
        new_post_body = post_json['messages'][0]['body']
        if old_post_body == None:
            old_post_body = new_post_body
        if new_post_body != old_post_body:
            # repost the post in Mastodon
            print("New post found!")
            print(new_post_body)
            try:
                reposter(new_post_body)
            except Exception as e:
                print(f"Error in Reposter: {e}")
            print("Post Reposted")
            #  get the post data
            post_data = parse_post(client, post_json)
            # update the google sheet
            values = [post_data['pos'], post_data['side'], post_data['ticker'], post_data['price'], post_data['timestamp'], post_data['bought_price']]
            update_sheet(values)
            print(post_data)    
            # update the old posy text
            old_post_body = new_post_body
        time.sleep(2)