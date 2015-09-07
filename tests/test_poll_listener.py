from webpage_listener import listener


def test_poll():
    e = listener.poll('https://www.google.com/', 'input')
    assert e is not None
    assert len(e) > 0