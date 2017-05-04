from unittest import TestCase

from mathcp.loop import Tickable, Loop


def once():
    i = 1
    return lambda: i - 1


class LoopTestCase(TestCase):
    def test_tick(self):
        class TestTickable(Tickable):
            def tick(self):
                raise Exception("tick")

        try:
            Loop(TestTickable()).run(1)
        except Exception as e:
            self.assertEqual(str(e), "tick")

    def test_chained_ticks(self):
        class TestTickable2(Tickable):
            def tick(self):
                raise Exception("tick2")

        class TestTickable1(Tickable):
            def tick(self):
                self._loop.add(TestTickable2())

        try:
            Loop(TestTickable1()).run(1)
        except Exception as e:
            self.assertEqual(str(e), "tick2")

    def test_tick_destroy_and_remove(self):
        class TestTickable(Tickable):
            def destroy(self):
                super().destroy()
                raise Exception("destroy")

            def tick(self):
                self.destroy()

        tickable = TestTickable()

        try:
            Loop(tickable).run(1)
        except Exception as e:
            self.assertEqual(str(e), "destroy")
            self.assertEqual(tickable._loop, None)
