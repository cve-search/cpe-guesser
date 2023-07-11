#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
from dynaconf import Dynaconf

# Configuration
settings = Dynaconf(
    settings_files=['../config/settings.yaml']
)

class CPEGuesser:
    def __init__(self):
        self.rdb = redis.Redis(host=settings.redis.host, port=settings.redis.port, db=8, decode_responses=True)

    def guessCpe(self, words):
        k = []
        for keyword in words:
            k.append(f"w:{keyword.lower()}")

        maxinter = len(k)
        cpes = []
        for x in reversed(range(maxinter)):
            ret = self.rdb.sinter(k[x])
            cpes.append(list(ret))
        result = set(cpes[0]).intersection(*cpes)

        ranked = []

        for cpe in result:
            rank = self.rdb.zrank('rank:cpe', cpe)
            ranked.append((rank, cpe))

        return sorted(ranked)
