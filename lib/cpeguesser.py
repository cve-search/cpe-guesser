#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis


class CPEGuesser:
    def __init__(self):
        self.rdb = redis.Redis(host='127.0.0.1', port=6379, db=8, decode_responses=True)

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
