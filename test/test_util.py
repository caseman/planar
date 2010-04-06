
def test_cached_property():
    from planar.util import cached_property

    class Thingy(object):
        not_cached_calls = 0
        cached_calls = 0

        @property
        def not_cached(self):
            """Nay"""
            self.not_cached_calls += 1
            return 'not cached'

        @cached_property
        def cached(self):
            """Yay"""
            self.cached_calls += 1
            return 'cached'
    
    thing = Thingy()
    assert thing.not_cached_calls == 0
    assert Thingy.not_cached.__doc__ == 'Nay'
    assert thing.cached_calls == 0
    assert Thingy.cached.__doc__ == 'Yay'

    not_cached_value = thing.not_cached
    assert thing.not_cached_calls == 1

    cached_value = thing.cached
    assert thing.cached_calls == 1

    assert not_cached_value == thing.not_cached
    assert thing.not_cached_calls == 2

    assert cached_value == thing.cached
    assert thing.cached_calls == 1

    assert not_cached_value == thing.not_cached
    assert thing.not_cached_calls == 3

    assert cached_value == thing.cached
    assert thing.cached_calls == 1

# vim: ai ts=4 sts=4 et sw=4 tw=78

