from asyncio import StreamWriter
from contextlib import contextmanager, ExitStack
from dataclasses import dataclass, field

from keysymdef import keysymdef


keys = {}
keys.update((name, code) for name, code, char in keysymdef)
keys.update((chr(char), code) for name, code, char in keysymdef if char)
keys['Del'] = keys['Delete']
keys['Esc'] = keys['Escape']
keys['Cmd'] = keys['Super_L']
keys['Alt'] = keys['Alt_L']
keys['Ctrl'] = keys['Control_L']
keys['Super'] = keys['Super_L']
keys['Shift'] = keys['Shift_L']
keys['Backspace'] = keys['BackSpace']


@dataclass
class Keyboard:
    """
    The virtual keyboard.
    """

    writer: StreamWriter = field(repr=False)

    @contextmanager
    def _hold(self, key: str):
        data = keys[key].to_bytes(4, 'big')
        self.writer.write(b'\x04\x01\x00\x00' + data)
        try:
            yield
        finally:
            self.writer.write(b'\x04\x00\x00\x00' + data)

    @contextmanager
    def hold(self, *keys: str):
        """
        Context manager that pushes the given keys on enter, and releases them (in reverse order) on exit.
        """

        with ExitStack() as stack:
            for key in keys:
                stack.enter_context(self._hold(key))
            yield

    def press(self, *keys: str):
        """
        Pushes all the given keys, and then releases them in reverse order.
        """

        with self.hold(*keys):
            pass

    def write(self, text: str):
        """
        Pushes and releases each of the given keys, one after the other.
        """

        for key in text:
            with self.hold(key):
                pass
