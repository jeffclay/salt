"""
Integration tests for the mac_desktop execution module.
"""

import pytest

pytestmark = [
    pytest.mark.slow_test,
    pytest.mark.destructive_test,
    pytest.mark.skip_if_not_root,
    pytest.mark.skip_unless_on_darwin,
]


@pytest.fixture(scope="module")
def desktop(modules):
    return modules.desktop


def test_get_output_volume(desktop):
    """
    Tests the return of get_output_volume.
    """
    ret = desktop.get_output_volume()
    assert ret is not None


def test_set_output_volume(desktop):
    """
    Tests the return of set_output_volume.
    """
    try:
        ret = desktop.get_output_volume()
        current_vol = ret
        to_set = 10
        if current_vol == str(to_set):
            to_set += 2
        ret = desktop.set_output_volume(str(to_set))
        new_vol = ret
        ret = desktop.get_output_volume()
        check_vol = ret
        assert new_vol == check_vol
    finally:
        # Set volume back to what it was before
        desktop.set_output_volume(current_vol)


def test_screensaver(desktop):
    """
    Tests the return of the screensaver function.
    """
    ret = desktop.screensaver()
    if "does not exist" in ret:
        pytest.skip("Skipping. Screensaver unavailable.")
    assert ret


def test_lock(desktop):
    """
    Tests the return of the lock function.
    """
    ret = desktop.lock()
    if "Unable to run" in ret:
        pytest.skip("Skipping. Unable to lock screen.")
    assert ret


def test_say(desktop):
    """
    Tests the return of the say function.
    """
    ret = desktop.say("hello", "world")
    assert ret
