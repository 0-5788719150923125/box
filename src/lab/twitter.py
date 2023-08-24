import os
import asyncio
import random
import time
import tweepy
import head
from utils import ad, bc

def orchestrate(config):
    asyncio.run(loop(config))

async def loop(config):
    while True:
        if random.random() < config.get("chance", 0.00059):
            topics = config.get("topics", ["AI alignment"])
            await tweet(
                await head.gen(
                    prefix=random.choice(topics),
                    max_new_tokens=59,
                    decay_after_length=12,
                    decay_factor=0.023,
                    mode="prompt",
                )
            )
        time.sleep(66.6)


async def tweet(message: str = "This is an automated test."):
    client = tweepy.Client(bearer_token=os.environ["TWITTERBEARERTOKEN"])

    client = tweepy.Client(
        consumer_key=os.environ["TWITTERCONSUMERKEY"],
        consumer_secret=os.environ["TWITTERCONSUMERSECRET"],
        access_token=os.environ["TWITTERACCESSTOKEN"],
        access_token_secret=os.environ["TWITTERACCESSTOKENSECRET"],
    )
    response = client.create_tweet(text=message)
    print(bc.CORE + "ONE@TWITTER: " + ad.TEXT + message)
