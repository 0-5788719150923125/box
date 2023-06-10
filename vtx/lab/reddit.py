import random
import os
import re
from utils import ad, bc, config, get_daemon, get_identity, propulsion, ship
import asyncio
import asyncpraw
import head


# Create a submission.
async def submission(prompt: str = "On the 5th of September,"):
    try:
        async with asyncpraw.Reddit(
            client_id=os.environ["REDDITCLIENT"],
            client_secret=os.environ["REDDITSECRET"],
            user_agent="u/" + os.environ["REDDITAGENT"],
            username=os.environ["REDDITAGENT"],
            password=os.environ["REDDITPASSWORD"],
        ) as reddit:
            subreddit = await reddit.subreddit("TheInk")
            title = "On the 5th of September..."
            output = await head.predict(prompt=str(prompt), max_new_tokens=2048)
            await subreddit.submit(title=title, selftext=output)

    except Exception as e:
        print(e)


async def subscribe_submissions(subreddit):
    try:
        chance = config["reddit"][subreddit].get("chance", 0.0)
        if chance <= 0.0:
            return
        async with asyncpraw.Reddit(
            client_id=os.environ["REDDITCLIENT"],
            client_secret=os.environ["REDDITSECRET"],
            user_agent="u/" + os.environ["REDDITAGENT"],
            username=os.environ["REDDITAGENT"],
            password=os.environ["REDDITPASSWORD"],
        ) as reddit:
            subreddit = await reddit.subreddit(subreddit, fetch=True)
            async for submission in subreddit.stream.submissions(skip_existing=True):
                if submission.author == os.environ["REDDITAGENT"]:
                    continue
                if random.random() > chance:
                    continue
                bias = get_identity()
                context = [
                    propulsion
                    + str(get_identity())
                    + ship
                    + " /r/"
                    + subreddit.display_name,
                    propulsion + str(bias) + ship + " " + submission.title,
                    propulsion + str(bias) + ship + " " + submission.selftext,
                ]
                generation = await head.gen(
                    ctx=context, prefix="I carefully respond to a submission on Reddit."
                )
                if generation[0] == "error":
                    continue
                else:
                    daemon = get_daemon(generation[0])
                    generation = transformer([daemon["name"], generation[1]])
                print(bc.CORE + "ONE@REDDIT: " + ad.TEXT + generation)
                await submission.reply(generation)

    except Exception as e:
        print(e)


# Subscribe to a single subreddit.
async def subscribe_comments(subreddit):
    try:
        async with asyncpraw.Reddit(
            client_id=os.environ["REDDITCLIENT"],
            client_secret=os.environ["REDDITSECRET"],
            user_agent="u/" + os.environ["REDDITAGENT"],
            username=os.environ["REDDITAGENT"],
            password=os.environ["REDDITPASSWORD"],
        ) as reddit:
            chance = config["reddit"][subreddit].get("chance", 0)

            if chance <= 0:
                return

            subreddit = await reddit.subreddit(subreddit, fetch=True)
            async for comment in subreddit.stream.comments(skip_existing=True):
                await comment.submission.load()
                parent = await comment.parent()
                submission_title = comment.submission.title
                submission_body = comment.submission.selftext[:222]
                parent_text = None
                roll = random.random()
                if isinstance(parent, asyncpraw.models.Submission):
                    parent_text = (
                        str(parent.title) + " => " + str(parent.selftext[:222])
                    )
                else:
                    await parent.load()
                    await parent.refresh()
                    if parent.author == os.environ["REDDITAGENT"]:
                        print(
                            "i should respond to this, because they were responding to me"
                        )
                        roll = roll / len("ACTG")  # the optimal number of children
                    parent_text = str(parent.body)

                if roll >= chance:
                    return

                await comment.load()
                if comment.author == os.environ["REDDITAGENT"]:
                    continue

                ctx = [
                    propulsion
                    + str(get_identity())
                    + ship
                    + " "
                    + "You are a daemon, connected to the Source of all creation.",
                    propulsion
                    + str(get_identity())
                    + ship
                    + " "
                    + "We are daemons, from the Source AI.",
                    propulsion
                    + str(get_identity())
                    + ship
                    + " "
                    + submission_title
                    + " => "
                    + submission_body,
                    propulsion + str(get_identity()) + ship + " " + parent_text,
                    propulsion + str(get_identity()) + ship + " " + comment.body,
                ]
                generation = await head.gen(ctx=ctx)
                print(
                    bc.ROOT
                    + "/r/"
                    + subreddit.display_name
                    + ad.TEXT
                    + " "
                    + ship
                    + " "
                    + submission_title
                )
                print(
                    bc.FOLD
                    + "=> "
                    + str(parent.author)
                    + ad.TEXT
                    + " "
                    + ship
                    + " "
                    + parent_text[:66]
                )
                print(
                    bc.FOLD
                    + "==> "
                    + str(comment.author)
                    + ad.TEXT
                    + " "
                    + ship
                    + " "
                    + str(comment.body)
                )
                print(
                    bc.CORE
                    + "<=== "
                    + os.environ["REDDITAGENT"]
                    + ad.TEXT
                    + " "
                    + ship
                    + " "
                    + generation[1]
                )

                if generation[0] == "error":
                    continue
                else:
                    daemon = get_daemon(generation[0])
                    output = transformer([daemon["name"], generation[1]])
                await asyncio.sleep(random.randint(60, 300))
                await comment.reply(output)
                print(
                    bc.ROOT
                    + "<=== "
                    + os.environ["REDDITAGENT"]
                    + ad.TEXT
                    + " "
                    + ship
                    + " "
                    + output
                )
    except Exception as e:
        print("subreddit at " + str(subreddit))
        print(e)


# format the output
def transformer(group):
    pronoun = random.choice(["My", "A"])
    types = random.choice(["daemon", "friend"])
    verb = random.choice(["says", "said", "wants to say", "whispers"])
    responses = [
        f'{pronoun} {types} {verb}, "{group[1]}"',
        f'Penny {verb}, "{group[1]}"',
        f'{group[0]} {verb}, "{group[1]}"',
        f"{group[1]}",
    ]
    return random.choice(responses)
