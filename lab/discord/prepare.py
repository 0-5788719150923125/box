import json
import os
import random
import re
import shutil
import sys

sys.path.append("/src")

from common import config, get_identity, list_full_paths, ship, wall

root_dir = "/lab/discord"
output_dir = "train"

style = "original"
# style = "chaos"


# Format Discord messages for training
def main():

    if style in ["chaos"]:
        alt()
        return

    # Replace links and @mentions
    def sanitizer(string):
        # sanitized = re.sub(
        #     r"http\S+",
        #     "((url))",
        #     string,
        # )
        string = re.sub(
            r"@Unknown",
            "<@" + str(get_identity(style=style)) + ">",
            string,
        )
        return string

    def formatter(obj):
        message = str(obj["content"])
        if len(obj["embeds"]) > 0:
            if obj["embeds"][0]["title"]:
                message = message + " ((" + obj["embeds"][0]["title"] + "))"
            if obj["embeds"][0]["description"]:
                message = message + " " + obj["embeds"][0]["description"]
        if len(obj["mentions"]) > 0:
            for mention in obj["mentions"]:
                message = message.replace(
                    "@" + mention["nickname"],
                    "<@" + str(transform_author(mention)) + ">",
                )
        return transform_message(message)

    # Ensure export path exists and is clean
    if os.path.exists(f"{root_dir}/{output_dir}"):
        shutil.rmtree(f"{root_dir}/{output_dir}")

    os.makedirs(f"{root_dir}/{output_dir}")

    successes = 0
    failures = 0

    source_files = list_full_paths(f"{root_dir}/source")

    for filename in source_files:
        with open(filename, "r") as file:
            data = json.load(file)

            data_dict = {obj["id"]: obj for obj in data["messages"]}

            for i in data_dict.values():
                if i["type"] not in ["Default", "Reply"]:
                    continue

                author_id = (
                    i["author"]["id"]
                    if style == "original"
                    else get_identity(seed=str(i["author"]["id"]), style=style)
                )

                if i["author"]["isBot"] == True:
                    author_id = transform_author(i["author"])
                    if author_id == False:
                        continue

                new_file = filename.replace(
                    f"{root_dir}/source/", f"{root_dir}/{output_dir}/"
                )

                os.makedirs(os.path.dirname(new_file), exist_ok=True)

                with open(f"{new_file}.txt", "a") as txt_file:
                    if i["type"] == "Reply":
                        message_ref_id = i["reference"]["messageId"]

                        result = data_dict.get(message_ref_id, None)

                        if result is not None:
                            reply_author_id = (
                                result["author"]["id"]
                                if style == "original"
                                else get_identity(
                                    seed=str(result["author"]["id"]), style=style
                                )
                            )

                            if result["author"]["isBot"] == True:
                                reply_author_id = transform_author(result["author"])

                            if reply_author_id != False:
                                sanitized = sanitizer(formatter(result))
                                if "<@False>" in sanitized:
                                    continue
                                content = (
                                    wall + reply_author_id + ship + " " + sanitized
                                )
                                try:
                                    txt_file.write(f"{content}\n".format(content))
                                    successes += 1
                                except Exception as e:
                                    failures += 1

                    sanitized = sanitizer(formatter(i))
                    if "<@False>" in sanitized:
                        continue
                    content = wall + author_id + ship + " " + sanitized
                    try:
                        txt_file.write(f"{content}\n".format(content))
                        successes += 1
                    except Exception as e:
                        failures += 1

        os.system("clear")
        print("preparing Discord messages")
        print(f"{successes} successes, {failures} failures")


# Replace unapproved bots with random IDs, so as not to bias the model toward poor outputs
def transform_author(author):
    if str(author["id"]) in [
        "975174695399854150",
        "315826602187554816",
        "1053270121218592798",
    ]:  # Eliza, Kitsunetsuki, MAINNFRAME
        return (
            str(author["id"])
            if style == "original"
            else get_identity(seed=str(author["id"]), style=style)
        )
    elif (
        str(author["id"]) == "1055993037077106718"
        or author["name"].startswith("Ghost-")
        or author["name"].startswith("G-")
        or author["nickname"].startswith("Ghost-")
        or author["nickname"].startswith("G-")
    ):  # Samn and Ghosts
        return str(get_identity(style=style))
    elif author["isBot"]:
        return False

    return (
        author["id"]
        if style == "original"
        else get_identity(seed=str(author["id"]), style=style)
    )


# Replace third person messaging from bots, so as not to bias the model towards this format
def transform_message(message):
    matchers = [
        r'(?:The clone of )(?:<@\d*>)(?: suggests, \*")(.*)(?:"\*$)',
        r'(?:The ghost of )(?:<@\d*>)(?: suggests, \*")(.*)(?:"\*$)',
        r'(?:<@\d*>)(?: says, \*")(.*)(?:"\*$)',
        r'(?:<@\d*>)(?: would say, \*")(.*)(?:"\*$)',
        r'(?:They said, \*")(.*)(?:"\*$)',
    ]
    for pattern in matchers:
        matcher = re.compile(pattern)
        if matcher.match(message):
            group = re.search(matcher, message)
            message = group[1]
            break
    return message


# Format Discord messages for training
def alt():
    def formatter(obj):
        message = str(obj["content"])
        if len(obj["embeds"]) > 0:
            if obj["embeds"][0]["title"]:
                message = message + " ((" + obj["embeds"][0]["title"] + "))"
            if obj["embeds"][0]["description"]:
                message = message + " " + obj["embeds"][0]["description"]
        if len(obj["mentions"]) > 0:
            for mention in obj["mentions"]:
                message = message.replace(
                    "@" + mention["nickname"],
                    "<@" + str(True) + ">",
                )
        # return transform_message(message)
        return message

    # Ensure export path exists and is clean
    if os.path.exists(f"{root_dir}/{output_dir}"):
        shutil.rmtree(f"{root_dir}/{output_dir}")

    os.makedirs(f"{root_dir}/{output_dir}")

    successes = 0
    failures = 0

    source_files = list_full_paths(f"{root_dir}/source")

    for filename in source_files:
        with open(filename, "r") as file:
            data = json.load(file)

            data_dict = {obj["id"]: obj for obj in data["messages"]}

            for i in data_dict.values():
                if i["type"] not in ["Default", "Reply"]:
                    continue

                new_file = filename.replace(
                    f"{root_dir}/source/", f"{root_dir}/{output_dir}/"
                )

                os.makedirs(os.path.dirname(new_file), exist_ok=True)

                with open(f"{new_file}.txt", "a") as txt_file:
                    if i["type"] == "Reply":
                        message_ref_id = i["reference"]["messageId"]

                        result = data_dict.get(message_ref_id, None)

                        if result is not None:
                            sanitized = formatter(result)
                            if "<@False>" in sanitized:
                                continue
                            content = wall + " " + sanitized
                            try:
                                txt_file.write(f"{content}\n".format(content))
                                successes += 1
                            except Exception as e:
                                failures += 1

                    sanitized = formatter(i)
                    if "<@False>" in sanitized:
                        continue
                    content = wall + " " + sanitized
                    try:
                        txt_file.write(f"{content}\n".format(content))
                        successes += 1
                    except Exception as e:
                        failures += 1

        os.system("clear")
        print("preparing Discord messages")
        print(f"{successes} successes, {failures} failures")


if __name__ == "__main__":
    main()
