#!/usr/bin/env python

"""
A healthcheck script for the mailer.
"""

import sys
from asyncio import run
from aiohttp import ClientSession

async def main():
    async with ClientSession() as session:
        req = await session.get('http://127.0.0.1:8080')
        if req.status != 200:
            sys.exit(1)

if __name__ == '__main__':
    run(main())
