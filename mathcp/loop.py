import time


class Tickable(object):
    """
    This should be sub-classed by classes that want to run in the Loop

    The destroy method should be used as destructor where you have to clean your instance,
    call to the super().destroy() is mandatory so the tickable object gets removed from the loop
    and garbage collected.
    """

    def __init__(self):
        self._loop = None

    @property
    def loop(self):
        return self._loop

    def set_loop(self, loop: 'Loop'):
        if self._loop:
            self._loop.remove(self)

        self._loop = loop

    def destroy(self) -> None:
        if self._loop:
            self._loop.remove(self)
            self._loop = None

    def tick(self) -> None:
        pass


class Loop(object):
    """
    This is a simple loop implementation which holds a list of tickable objects.
    On each loop every tickable object tick method is called.
    """

    def __init__(self, *args):
        self._tickables = []

        for tickable in args:
            self.add(tickable)

    def add(self, tickable: Tickable) -> None:
        tickable.set_loop(self)
        self._tickables.append(tickable)

    def remove(self, tickable: Tickable) -> None:
        self._tickables.remove(tickable)

    def run(self, loops=0, sleep=0.01) -> None:
        i = 0

        while not loops or i < loops:
            for tickable in self._tickables:
                tickable.tick()

            time.sleep(sleep)

            if loops:
                i += 1
