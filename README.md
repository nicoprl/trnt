# trnt

Python CLI for managing torrents using transmission-cli and torrentapi.org 

## Prerequisites

Python 3.x
[transmission-cli](https://doc.ubuntu-fr.org/transmission#transmission-cli)

## Installing

`git clone https://github.com/nicoprl/trnt.git`
Add the directory to your PATH

## Usage
```
USAGE:

torrent.py [-s search_string] [-l] [-d torrent_id] [-dl] [-remove torrent_id] [--clear] [--magnet magnet_link] [--logs]

DESCRIPTION:

-s search_string      Search torrentapi.org for search_string
-l                    List torrents in shopping list (shopping_list.json)
-d torrent_id         Download torrent with torrent_id
-dl                   Download aLl torrents in shopping list
-r torrent_id         Remove torrent_id from shopping list
--clear               empty shopping list
--magnet magnet_link  download torrent with magnet_link
--logs                show logs
```
## Exemple

Search a torrent

`trnt -s "get.out.2017"`

List all torrents in the shopping list

`trnt -l`

Download all stored torrents

`trnt -dl'
