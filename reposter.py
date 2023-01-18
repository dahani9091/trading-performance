from mastodon import Mastodon
import config

def reposter(post):
    # Initialize Mastodon client
    mastodon = Mastodon(
        access_token = "2hdmjp5510Kg_XrWPVgTqgTHnmEvP7l3IK1TyZ2KY2Y",
        api_base_url = "https://arsenalfc.social/"
    )


    # Publish the post
    mastodon.status_post(status=post)


