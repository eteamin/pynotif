
class AsyncListOfTupleIteration:
    def __init__(self, _list):
        self.list = _list
        self.i = 0

    async def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            item = self.list[self.i]
            self.i += 1
            return item
        except IndexError:
            raise StopAsyncIteration
