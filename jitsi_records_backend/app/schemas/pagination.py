class Pagination:
    def __init__(self, offset: int = 0, limit: int = 20):
        self.skip = offset
        self.limit = limit

    def dict(self):
        return {'skip': self.skip, 'limit': self.limit}