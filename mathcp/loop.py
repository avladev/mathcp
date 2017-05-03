class Tickable(object):
    def __init__(self):
        self.loop = None

    def destroy(self):
        if self.loop:
            self.loop.remove(self)
            self.loop = None

    def tick(self):
        pass


class Loop(object):
    def __init__(self, *args):
        self.tickables = []

        for tickable in args:
            self.add(tickable)

    def add(self, tickable: Tickable):
        tickable.loop = self
        self.tickables.append(tickable)

    def remove(self, tickable: Tickable):
        self.tickables.remove(tickable)

    def run(self, loops=0):
        i = 0

        while not loops or i < loops:
            for tickable in self.tickables:
                tickable.tick()

            i += 1
