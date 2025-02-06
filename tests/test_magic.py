import pytest
from unittest.mock import MagicMock
from agentsystem.app.magic import MMB, MagicMessageBus, generic_coupler


class TestMagic:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.magic = MMB
        self.magic.state = {}
        self.magic.subscribers = {}
        print("Setup done")

    def test_subscribe_key_not_exists(self):
        key = "test_key"
        callback = MagicMock()

        self.magic.subscribe(key, callback)

        assert (
            key in self.magic.subscribers
        ), "The key should be added to the subscribers dictionary."
        assert (
            len(self.magic.subscribers[key]) == 1
        ), "The callback should be added to the subscribers list."

    def test_subscribe_key_exists(self):
        key = "test_key"
        callback1 = MagicMock()
        callback2 = MagicMock()

        self.magic.subscribers[key] = [callback1]

        self.magic.subscribe(key, callback2)

        assert (
            len(self.magic.subscribers[key]) == 2
        ), "The second callback should be added to the subscribers list."

    def test_subscribe_multiple_keys(self):
        key1 = "key1"
        key2 = "key2"
        callback = MagicMock()

        self.magic.subscribe(key1, callback)
        self.magic.subscribe(key2, callback)

        assert (
            key1 in self.magic.subscribers
        ), "The first key should be added to the subscribers dictionary."
        assert (
            key2 in self.magic.subscribers
        ), "The second key should be added to the subscribers dictionary."
        assert (
            len(self.magic.subscribers[key1]) == 1
        ), "The callback should be added to the subscribers list of the first key."
        assert (
            len(self.magic.subscribers[key2]) == 1
        ), "The callback should be added to the subscribers list of the second key."

    # Append to the existing test file

    def test_set_state(self):
        key = "test_key"
        value = "test_value"

        self.magic.set_state(key, value)

        assert (
            key in self.magic.state
        ), "The key should be added to the state dictionary."
        assert (
            self.magic.state[key] == value
        ), "The value should be set in the state dictionary."

    def test_get_state(self):
        key = "test_key"
        value = "test_value"
        self.magic.state[key] = value

        result = self.magic.get_state(key)

        assert (
            result == value
        ), "The value should be retrieved from the state dictionary."

    def test_unsubscribe(self):
        key = "test_key"
        callback = MagicMock()

        self.magic.subscribe(key, callback)
        self.magic.unsubscribe(key, callback)

        assert (
            len(self.magic.subscribers[key]) == 0
        ), "The callback should be removed from the subscribers list."

    def test_notify_subscribers(self):
        key = "test_key"
        value = "test_value"
        callback = MagicMock()

        self.magic.subscribe(key, callback)
        self.magic.set_state(key, value)

        callback.assert_called_once_with(value, key)

    def test_set_prefix_collection(self):
        prefix = "test_"
        key1 = "test_key1"
        key2 = "test_key2"
        value1 = "value1"
        value2 = "value2"

        self.magic.set_state(key1, value1)
        self.magic.set_state(key2, value2)
        self.magic.set_prefix_collection(prefix)

        prefix_collection = self.magic.get_state(prefix)

        assert (
            key1.removeprefix(prefix),
            value1,
        ) in prefix_collection.items(), (
            "The first key-value pair should be in the prefix collection."
        )
        assert (
            key2.removeprefix(prefix),
            value2,
        ) in prefix_collection.items(), (
            "The second key-value pair should be in the prefix collection."
        )

    def test_bracket_notation(self):
        key = "test_key"
        value = "test_value"

        self.magic[key] = value

        assert (
            key in self.magic.state
        ), "The key should be added to the state dictionary."
        assert (
            self.magic.state[key] == value
        ), "The value should be set in the state dictionary."

        result = self.magic[key]

        assert (
            result == value
        ), "The value should be retrieved from the state dictionary."

    def test_magic_message_bus_init(self):
        magic = MagicMessageBus()
        assert magic.state == {}, "State should be an empty dictionary"
        assert magic.subscribers == {}, "Subscribers should be an empty dictionary"

    def test_magic_message_bus_set_state_notify_subscribers(self):
        key = "test_key"
        value = "test_value"
        callback = MagicMock()

        self.magic.subscribe(key, callback)
        self.magic.set_state(key, value)

        callback.assert_called_once_with(value, key)

    def test_magic_message_bus_get_state_key_not_exists(self):
        key = "test_key"
        result = self.magic.get_state(key)
        assert result is None, "Should return None for non-existent key"

    def test_prefix_callback_called_on_set_state(self):
        prefix = "test_"
        key1 = "test_key1"
        key2 = "test_key2"
        value1 = "value1"
        value2 = "value2"

        # callback = MagicMock()
        # self.magic.subscribe(self.magic, callback)
        callback = MagicMock()
        old = self.magic.create_prefix_callback
        self.magic.create_prefix_callback = MagicMock(return_value=callback)
        self.magic.set_prefix_collection(prefix)
        callback.assert_called_with(None, prefix)

        self.magic.set_state(key1, value1)
        callback.assert_called_with(value1, key1)

        self.magic.set_state(key2, value2)
        callback.assert_called_with(value2, key2)
        self.magic.create_prefix_callback = old

    def test_magic_message_bus_set_prefix_collection_update(self):
        prefix = "test_"
        key1 = "test_key1"
        key2 = "test_key2"
        value1 = "value1"
        value2 = "value2"

        self.magic.set_state(key1, value1)
        self.magic.set_state(key2, value2)
        self.magic.set_prefix_collection(prefix)

        prefix_collection = self.magic.get_state(prefix)

        assert (
            key1.removeprefix(prefix),
            value1,
        ) in prefix_collection.items(), (
            "The first key-value pair should be in the prefix collection."
        )
        assert (
            key2.removeprefix(prefix),
            value2,
        ) in prefix_collection.items(), (
            "The second key-value pair should be in the prefix collection."
        )

        # Update a value
        new_value1 = "new_value1"
        self.magic.set_state(key1, new_value1)

        prefix_collection = self.magic.get_state(prefix)
        assert (
            key1.removeprefix(prefix),
            new_value1,
        ) in prefix_collection.items(), (
            "The updated key-value pair should be in the prefix collection."
        )
        assert (
            key1.removeprefix(prefix),
            new_value1,
        ) in prefix_collection.items(), (
            "The updated key-value pair should be in the prefix collection."
        )

    def test_unset_prefix_collection(self):
        prefix = "test_"
        key1 = "test_key1"
        key2 = "test_key2"
        value1 = "value1"
        value2 = "value2"

        self.magic.set_state(key1, value1)
        self.magic.set_state(key2, value2)
        self.magic.set_prefix_collection(prefix)

        prefix_collection = self.magic.get_state(prefix)
        assert (
            key1.removeprefix(prefix),
            value1,
        ) in prefix_collection.items(), (
            "The first key-value pair should be in the prefix collection."
        )
        assert (
            key2.removeprefix(prefix),
            value2,
        ) in prefix_collection.items(), (
            "The second key-value pair should be in the prefix collection."
        )

        self.magic.unset_prefix_collection(prefix)

        prefix_collection = self.magic.get_state(prefix)
        assert (
            prefix not in self.magic.subscribers
        ), "The prefix callback should be unsubscribed."
        assert (
            prefix not in self.magic.state
        ), "The prefix collection should be removed from the state dictionary."

    def test_magic_message_bus_generic_coupler(self):
        class TestObject:
            pass

        obj = TestObject()
        key = "test_key"
        value = "test_value"

        generic_coupler(obj, key)
        self.magic.set_state(key, value)

        assert getattr(obj, key) == value, "The value should be set on the object."

        # Test that the value is updated when the state is updated
        new_value = "new_value"
        self.magic.set_state(key, new_value)
        assert (
            getattr(obj, key) == new_value
        ), "The value should be updated on the object."


if __name__ == "__main__":
    pytest.main()
