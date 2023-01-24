from mastodon import Mastodon
import config

def reposter(post):
    # Initialize Mastodon client
    mastodon = Mastodon(
        access_token = config.mastodon_access_token,
        api_base_url = "https://arsenalfc.social/"
    )


    # Publish the post
    mastodon.status_post(status=post)


