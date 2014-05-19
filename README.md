## Garena DotA League Bot

This is some very old and messy code i wrote when learning Python/Programming about five years ago.

Bot supports joining Garena *LAN* rooms,
however it only implements a very small subset of network protocol,
mostly sending messages and kicking players.
Authentication is semi-manual, and relies on using sniffer software to capture packet from official client.
This packet is stored in database and used by bot to connect to room servers.
P2P protocol that is used for gaming and private chats is more or less implemented,
and I even remember being able to actually play Warcraft 3 hosted by GHost++ on a server.
Was pretty slow though, since its Python, and the way I implemented resending packes is probably very inefficient.

Bot supports different user groups, and some commands require certain group membership,
or may work differently if used is a member of some group.

Leagues are divided by chat rooms, each room having its own memberships, games, scores etc.

Multiple Garena accounts can work in one room to avoid anti-spam feature.

Tests are heavily hardcoded and probably dont even work.

Django ORM is used for database access and Twisted for networking. Jinja2 for templates.

This bot was working all these years, and is still up in *Allstars Mortals Room* of the Kazakhstan section.
Live database contains about 70 thousand games total. Current online is about 30-50 players.
