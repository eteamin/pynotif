import asyncio
import asyncio_redis


async def foo():
    conn = await asyncio_redis.Connection.create(db=12)
    v = await conn.get("bye")
    print(v)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(foo())
