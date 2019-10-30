#!/usr/bin/python3

import json
import time
import os
import sys
import argparse
import subprocess
import urllib.request
import logging
from logging.handlers import RotatingFileHandler

# logs (critical > error > warning > info > debug)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s  %(levelname)s  %(type)s  %(message)s")
# log file handler
fileHandler = RotatingFileHandler(sys.path[0] + "/logs.log", "a", 10000000, 4)
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
log.addHandler(fileHandler)
# console handler
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
log.addHandler(streamHandler)


def main():
    # argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-s', required=False, metavar='search string', help='Search torrentapi.org for search_string')
    parser.add_argument('-l', required=False, action="store_true", help='List torrents in shopping list (shopping_list.json)')
    parser.add_argument('-d', required=False, metavar='torrentID', help='Download torrent with torrent id')
    parser.add_argument('-dl', required=False, action="store_true", help='Download aLl torrents in shopping list')
    parser.add_argument('-r', required=False, metavar='torrentID', help='Remove torrent_id from shopping list')
    parser.add_argument('--clear', required=False, action="store_true", help='empty shopping list')
    parser.add_argument('--magnet', required=False, metavar='magnetlink', help='download torrent with magnet link')
    parser.add_argument('--logs', required=False, action="store_true", help='show logs')
    args = parser.parse_args()

    URL = "https://torrentapi.org/pubapi_v2.php"
    APP_ID = "trnt"
    HEADERS = {"user-agent": "trnt"}

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if args.s is not None:
        try:
            search_string = args.s
        except IndexError:
            log.error("No search_string provided", extra={"type": "[APP]"})
            sys.exit(1)
        found = search_torrent(search_string, URL, APP_ID, HEADERS, log)
        downloadOrStore(found, log)
    elif args.l:
        showShoppingList()
    elif args.d is not None:
        try:
            torrent_id = args.d
        except IndexError:
            log.error("No torrent_id provided", extra={"type": "[APP]"})
            sys.exit(1)
        shopping_list = json.load(open(sys.path[0] + "/shopping_list.json"))
        torrent_name = shopping_list[torrent_id]["name"]
        magnet_link = shopping_list[torrent_id]["magnet"]
        downloadTorrent(torrent_id, torrent_name, magnet_link, True, log)
    elif args.dl:
        downloadList(log)
    elif args.clear:
        emptyShoppingList(log)
    elif args.r is not None:
        torrent_id = args.r
        removeTorrentFromList(torrent_id, log)
    elif args.magnet is not None:
        magnet_link = args.magnet
        downloadTorrent(9999, "", magnet_link, True, log)
    elif args.logs:
        showLogs()


def doc():
    doc = """
    USAGE:

    trnt [-s search_string] [-l] [-d torrent_id] [-dl] [-remove torrent_id] [--clear] [--magnet magnet_link] [--logs]

    DESCRIPTION:

    -s search_string      Search torrentapi.org for search_string
    -l                    List torrents in shopping list (shopping_list.json)
    -d torrent_id         Download torrent with torrent_id
    -dl                   Download aLl torrents in shopping list
    -r torrent_id         Remove torrent_id from shopping list
    --clear               empty shopping list
    --magnet magnet_link  download torrent with magnet_link
    --logs                show logs
    """

    return doc


def showLogs():
    with open(sys.path[0] + "/logs.log") as logs:
        print(logs.read())


def get_token(url, app_id, headers):
    fullUrl = url + "?app_id=" + app_id + "&get_token=get_token"
    r = urllib.request.Request(fullUrl, headers=headers)
    with urllib.request.urlopen(r) as rep:
        token = json.loads(rep.read().decode("utf-8"))
        return token["token"]


def search_torrent(search_string, url, app_id, headers, log):
    found = {}

    try:
        token = get_token(url, app_id, headers)
    except Exception as e:
        log.error("Error getting token", extra={"type": "[APP]"})
        log.error(e, extra={"type": "[APP]"})
        sys.exit(1)
    else:
        log.debug("Got token %s", token, extra={"type": "[APP]"})
        time.sleep(0.5)

        fullUrl = "{0}?app_id={1}&token={2}&mode=search&search_string={3}&sort=seeders".format(
            url, app_id, token, search_string
        )
        log.debug(search_string, extra={"type": "[SEARCH]"})
        try:
            r = urllib.request.Request(fullUrl, headers=headers)
            with urllib.request.urlopen(r) as rep:
                results = json.loads(rep.read().decode("utf-8"))
                if "error_code" in results:
                    log.error(
                        "error_code: %s", results["error_code"], extra={"type": "[SEARCH]"}
                    )
                    log.error("error: %s", results["error"], extra={"type": "[SEARCH]"})
                    sys.exit(1)

                torrents = results["torrent_results"]

                for e in torrents:
                    torrentInfos = []

                    index = torrents.index(e)
                    filename = e["filename"]
                    magnet_link = e["download"]

                    torrentInfos.append(filename)
                    torrentInfos.append(magnet_link)

                    found[index] = torrentInfos
        except HTTPError as err_http:
            log.error(err_http, extra={"type": "[APP]"})
            sys.exit(1)
        except Exception as err_http_gen:
            log.error(err_http_gen, extra={"type": "[APP]"})
            sys.exit(1)

        return found


def downloadOrStore(found, log):
    for key, value in found.items():
        print("{0} : {1}".format(key, value[0]))

    choice = input("download/store/quit ? (d [index], s [index], q) ")

    try:
        if choice[0] == "d" or choice[0] == "s":
            try:
                action = choice.split(" ")[0]
                index = int(choice.split(" ")[1])
            except:
                log.error("choice: invalid input", extra={"type": "[APP]"})
                downloadOrStore(found, log)
            else:
                try:
                    torrent_name = found[index][0]
                    magnet_link = found[index][1]
                except KeyError:
                    log.error(
                        "Invalid input: index %s does not exist",
                        index,
                        extra={"type": "[APP]"},
                    )
                    downloadOrStore(found, log)
                else:
                    if action == "d":
                        downloadTorrent(9999, torrent_name, magnet_link, True, log)
                    elif action == "s":
                        addTorrentToList(torrent_name, magnet_link, log)
        elif choice[0] == "q":
            sys.exit(0)
        else:
            log.error("choice: invalid input", extra={"type": "[APP]"})
            downloadOrStore(found, log)
    except IndexError:
        log.error("choice: invalid input", extra={"type": "[APP]"})
        downloadOrStore(found, log)


def addTorrentToList(torrent_name, magnet_link, log):
    with open(sys.path[0] + "/shopping_list.json") as json_list:
        shopping_list = json.load(json_list)
        if len(shopping_list) == 0:
            key = 0
        else:
            key = int(max(list(shopping_list.keys()))) + 1
        timestp = int(time.time())
        shopping_list[key] = {
            "name": torrent_name,
            "magnet": magnet_link,
            "added": timestp,
        }
        with open(sys.path[0] + "/shopping_list.json", "w") as outFile:
            json.dump(shopping_list, outFile)
            log.info(
                "%s added to shopping list",
                torrent_name,
                extra={"type": "[SHOPPING LIST]"},
            )


def showShoppingList():
    with open(sys.path[0] + "/shopping_list.json") as json_list:
        shopping_list = json.load(json_list)
        for key, value in sorted(shopping_list.items()):
            print(key, value["name"])


def emptyShoppingList(log):
    with open(sys.path[0] + "/shopping_list.json") as json_list:
        shopping_list = json.load(json_list)
        shopping_list.clear()
        with open(sys.path[0] + "/shopping_list.json", "w") as outFile:
            json.dump(shopping_list, outFile)
            log.info("shopping list cleared", extra={"type": "[SHOPPING LIST]"})


def downloadTorrent(torrent_id, torrent_name, magnet_link, stopWhenEnded, log):
    try:
        log.info(torrent_name, extra={"type": "[DOWNLOAD]"})
        log.info(magnet_link, extra={"type": "[DOWNLOAD]"})
        print("Starting download %s" % torrent_name)
        if stopWhenEnded:
            stopScriptPath = sys.path[0] + "/" + "stop_transmission.sh"
            subprocess.call(["transmission-cli", "-f", stopScriptPath, magnet_link])
        else:
            subprocess.call(["transmission-cli", magnet_link])
        if torrent_id != 9999:
            removeTorrentFromList(torrent_id, log)
    except Exception as e:
        log.error(e, extra={"type": "[APP]"})
        sys.exit(1)


def removeTorrentFromList(torrent_id, log):
    with open(sys.path[0] + "/shopping_list.json") as json_list:
        shopping_list = json.load(json_list)
        try:
            name = shopping_list[torrent_id]["name"]
            log.info(
                "%s removed from shopping list", name, extra={"type": "[SHOPPING LIST]"}
            )
            del shopping_list[torrent_id]
        except KeyError as e:
            log.error(
                "torrent_id %s does not exist in shopping_list",
                torrent_id,
                extra={"type": "[APP]"},
            )
            log.error(e)

        with open(sys.path[0] + "/shopping_list.json", "w") as outFile:
            json.dump(shopping_list, outFile)


def downloadList(log):
    with open(sys.path[0] + "/shopping_list.json") as json_list:
        shopping_list = json.load(json_list)
        log.info(
            "Starting download shopping list ...", extra={"type": "[SHOPPING LIST]"}
        )
        for key, value in shopping_list.items():
            downloadTorrent(key, value["name"], value["magnet"], False, log)
        log.info(
            "All items in shopping list downloaded", extra={"type": "[SHOPPING LIST]"}
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(1)
