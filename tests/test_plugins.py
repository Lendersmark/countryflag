"""
Comprehensive tests for the plugin system.

This module contains tests for plugin registration, retrieval, unregistration,
and error handling, including edge cases and type correctness.
"""

from typing import List, Optional

import pytest

from countryflag.core.exceptions import PluginError
from countryflag.core.models import CountryInfo
from countryflag.plugins import (
    BasePlugin,
    get_plugin,
    get_registered_plugins,
    register_plugin,
    unregister_plugin,
)


class DummyPlugin(BasePlugin):
    """Lightweight dummy plugin implementation for testing."""

    def __init__(self, name: str = "dummy"):
        """Initialize the dummy plugin with a name for identification."""
        self._name = name

    def get_country_info(self, name: str) -> Optional[CountryInfo]:
        """Return None for all country info requests."""
        return None

    def get_supported_countries(self) -> List[CountryInfo]:
        """Return empty list of supported countries."""
        return []

    def get_supported_regions(self) -> List[str]:
        """Return empty list of supported regions."""
        return []

    def get_countries_by_region(self, region: str) -> List[CountryInfo]:
        """Return empty list for any region query."""
        return []

    def convert_country_name(self, name: str, to_format: str) -> str:
        """Return empty string for any conversion request."""
        return ""

    def get_flag(self, country_name: str) -> Optional[str]:
        """Return None for all flag requests."""
        return None

    def reverse_lookup(self, flag_emoji: str) -> Optional[str]:
        """Return None for all reverse lookup requests."""
        return None


class CustomDummyPlugin(BasePlugin):
    """Another dummy plugin implementation for testing multiple plugins."""

    def get_country_info(self, name: str) -> Optional[CountryInfo]:
        if name.lower() == "test":
            return CountryInfo(
                name="Test Country",
                iso2="TC",
                iso3="TCO",
                official_name="Test Country Official",
                region="Test Region",
            )
        return None

    def get_supported_countries(self) -> List[CountryInfo]:
        return [
            CountryInfo(
                name="Test Country",
                iso2="TC",
                iso3="TCO",
                official_name="Test Country Official",
                region="Test Region",
            )
        ]

    def get_supported_regions(self) -> List[str]:
        return ["Test Region"]

    def get_countries_by_region(self, region: str) -> List[CountryInfo]:
        if region == "Test Region":
            return self.get_supported_countries()
        return []

    def convert_country_name(self, name: str, to_format: str) -> str:
        if name.lower() == "test country" and to_format == "ISO2":
            return "TC"
        return "not found"

    def get_flag(self, country_name: str) -> Optional[str]:
        if country_name.lower() == "test country":
            return "🏁"
        return None

    def reverse_lookup(self, flag_emoji: str) -> Optional[str]:
        if flag_emoji == "🏁":
            return "Test Country"
        return None


@pytest.fixture
def clean_plugin_registry():
    """Ensure clean plugin registry state for each test."""
    # Clear any existing plugins before test
    registered_plugins = get_registered_plugins().copy()
    for plugin_name in registered_plugins:
        try:
            unregister_plugin(plugin_name)
        except PluginError:
            pass

    yield

    # Clean up after test
    registered_plugins = get_registered_plugins().copy()
    for plugin_name in registered_plugins:
        try:
            unregister_plugin(plugin_name)
        except PluginError:
            pass


@pytest.fixture
def dummy_plugin():
    """Create a dummy plugin instance for testing."""
    return DummyPlugin()


@pytest.fixture
def custom_dummy_plugin():
    """Create a custom dummy plugin instance for testing."""
    return CustomDummyPlugin()


class TestPluginRegistration:
    """Test plugin registration functionality."""

    def test_register_plugin_success(self, clean_plugin_registry, dummy_plugin):
        """Test successful plugin registration."""
        plugin_name = "test_plugin"
        register_plugin(plugin_name, dummy_plugin)

        assert plugin_name in get_registered_plugins()
        assert len(get_registered_plugins()) == 1

    def test_register_multiple_plugins(self, clean_plugin_registry):
        """Test registering multiple plugins."""
        plugins = [(f"plugin_{i}", DummyPlugin(f"plugin_{i}")) for i in range(5)]

        for name, plugin in plugins:
            register_plugin(name, plugin)

        registered = get_registered_plugins()
        assert len(registered) == 5
        for name, _ in plugins:
            assert name in registered

    def test_register_duplicate_plugin_raises_error(
        self, clean_plugin_registry, dummy_plugin
    ):
        """Test that registering a duplicate plugin raises PluginError."""
        plugin_name = "duplicate_test"
        register_plugin(plugin_name, dummy_plugin)

        with pytest.raises(PluginError) as excinfo:
            register_plugin(plugin_name, dummy_plugin)

        assert f"Plugin '{plugin_name}' is already registered" in str(excinfo.value)
        assert excinfo.value.plugin_name == plugin_name

    def test_register_many_plugins(self, clean_plugin_registry):
        """Test registering many plugins (edge case for memory/performance)."""
        num_plugins = 100
        for i in range(num_plugins):
            name = f"bulk_plugin_{i}"
            register_plugin(name, DummyPlugin(name))

        assert len(get_registered_plugins()) == num_plugins

        # Verify all plugins are accessible
        for i in range(num_plugins):
            name = f"bulk_plugin_{i}"
            plugin = get_plugin(name)
            assert isinstance(plugin, BasePlugin)


class TestPluginRetrieval:
    """Test plugin retrieval functionality."""

    def test_get_plugin_success(self, clean_plugin_registry, dummy_plugin):
        """Test successful plugin retrieval."""
        plugin_name = "retrieval_test"
        register_plugin(plugin_name, dummy_plugin)

        retrieved_plugin = get_plugin(plugin_name)
        assert retrieved_plugin is dummy_plugin
        assert isinstance(retrieved_plugin, BasePlugin)

    def test_get_plugin_type_correctness(
        self, clean_plugin_registry, custom_dummy_plugin
    ):
        """Test that retrieved plugin maintains correct type."""
        plugin_name = "type_test"
        register_plugin(plugin_name, custom_dummy_plugin)

        retrieved_plugin = get_plugin(plugin_name)
        assert isinstance(retrieved_plugin, BasePlugin)
        assert isinstance(retrieved_plugin, CustomDummyPlugin)
        assert retrieved_plugin is custom_dummy_plugin

    def test_get_unknown_plugin_raises_error(self, clean_plugin_registry):
        """Test that getting an unknown plugin raises PluginError."""
        unknown_name = "nonexistent_plugin"

        with pytest.raises(PluginError) as excinfo:
            get_plugin(unknown_name)

        assert f"Plugin '{unknown_name}' is not registered" in str(excinfo.value)
        assert excinfo.value.plugin_name == unknown_name

    def test_get_registered_plugins_empty(self, clean_plugin_registry):
        """Test getting registered plugins when none are registered."""
        registered = get_registered_plugins()
        assert isinstance(registered, list)
        assert len(registered) == 0

    def test_get_registered_plugins_with_plugins(self, clean_plugin_registry):
        """Test getting registered plugins when some are registered."""
        plugin_names = ["plugin_a", "plugin_b", "plugin_c"]

        for name in plugin_names:
            register_plugin(name, DummyPlugin(name))

        registered = get_registered_plugins()
        assert isinstance(registered, list)
        assert len(registered) == len(plugin_names)
        assert set(registered) == set(plugin_names)


class TestPluginUnregistration:
    """Test plugin unregistration functionality."""

    def test_unregister_plugin_success(self, clean_plugin_registry, dummy_plugin):
        """Test successful plugin unregistration."""
        plugin_name = "unregister_test"
        register_plugin(plugin_name, dummy_plugin)
        assert plugin_name in get_registered_plugins()

        unregister_plugin(plugin_name)
        assert plugin_name not in get_registered_plugins()
        assert len(get_registered_plugins()) == 0

    def test_unregister_unknown_plugin_raises_error(self, clean_plugin_registry):
        """Test that unregistering an unknown plugin raises PluginError."""
        unknown_name = "nonexistent_plugin"

        with pytest.raises(PluginError) as excinfo:
            unregister_plugin(unknown_name)

        assert f"Plugin '{unknown_name}' is not registered" in str(excinfo.value)
        assert excinfo.value.plugin_name == unknown_name

    def test_unregister_twice_raises_error(self, clean_plugin_registry, dummy_plugin):
        """Test that unregistering the same plugin twice raises PluginError."""
        plugin_name = "double_unregister_test"
        register_plugin(plugin_name, dummy_plugin)

        # First unregistration should succeed
        unregister_plugin(plugin_name)
        assert plugin_name not in get_registered_plugins()

        # Second unregistration should fail
        with pytest.raises(PluginError) as excinfo:
            unregister_plugin(plugin_name)

        assert f"Plugin '{plugin_name}' is not registered" in str(excinfo.value)
        assert excinfo.value.plugin_name == plugin_name

    def test_get_plugin_after_unregistration_raises_error(
        self, clean_plugin_registry, dummy_plugin
    ):
        """Test that getting a plugin after unregistration raises PluginError."""
        plugin_name = "post_unregister_test"
        register_plugin(plugin_name, dummy_plugin)

        # Verify plugin is registered and retrievable
        retrieved_plugin = get_plugin(plugin_name)
        assert retrieved_plugin is dummy_plugin

        # Unregister plugin
        unregister_plugin(plugin_name)

        # Attempt to get plugin should fail
        with pytest.raises(PluginError) as excinfo:
            get_plugin(plugin_name)

        assert f"Plugin '{plugin_name}' is not registered" in str(excinfo.value)
        assert excinfo.value.plugin_name == plugin_name


class TestPluginEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_register_unregister_register_cycle(
        self, clean_plugin_registry, dummy_plugin
    ):
        """Test registering, unregistering, and re-registering the same plugin."""
        plugin_name = "cycle_test"

        # Register
        register_plugin(plugin_name, dummy_plugin)
        assert plugin_name in get_registered_plugins()
        retrieved = get_plugin(plugin_name)
        assert retrieved is dummy_plugin

        # Unregister
        unregister_plugin(plugin_name)
        assert plugin_name not in get_registered_plugins()

        # Re-register (should work fine)
        new_plugin = DummyPlugin("new_instance")
        register_plugin(plugin_name, new_plugin)
        assert plugin_name in get_registered_plugins()
        retrieved = get_plugin(plugin_name)
        assert retrieved is new_plugin
        assert retrieved is not dummy_plugin

    def test_plugin_name_case_sensitivity(self, clean_plugin_registry, dummy_plugin):
        """Test that plugin names are case-sensitive."""
        register_plugin("TestPlugin", dummy_plugin)

        # Should be able to register with different case
        register_plugin("testplugin", DummyPlugin("lowercase"))
        register_plugin("TESTPLUGIN", DummyPlugin("uppercase"))

        assert len(get_registered_plugins()) == 3
        assert "TestPlugin" in get_registered_plugins()
        assert "testplugin" in get_registered_plugins()
        assert "TESTPLUGIN" in get_registered_plugins()

    def test_plugin_with_special_characters_in_name(
        self, clean_plugin_registry, dummy_plugin
    ):
        """Test plugin registration with special characters in name."""
        special_names = [
            "plugin-with-dashes",
            "plugin_with_underscores",
            "plugin.with.dots",
            "plugin with spaces",
            "plugin123",
            "123plugin",
        ]

        for name in special_names:
            register_plugin(name, DummyPlugin(name))

        registered = get_registered_plugins()
        assert len(registered) == len(special_names)
        for name in special_names:
            assert name in registered
            plugin = get_plugin(name)
            assert isinstance(plugin, BasePlugin)

    def test_empty_plugin_name_handling(self, clean_plugin_registry, dummy_plugin):
        """Test handling of empty plugin name."""
        # Empty string should be a valid plugin name
        register_plugin("", dummy_plugin)
        assert "" in get_registered_plugins()
        retrieved = get_plugin("")
        assert retrieved is dummy_plugin

    def test_none_plugin_name_handling(self, clean_plugin_registry, dummy_plugin):
        """Test that None as plugin name is handled (even though not recommended)."""
        # None is actually accepted as a plugin name in the current implementation
        register_plugin(None, dummy_plugin)  # type: ignore
        assert None in get_registered_plugins()
        retrieved = get_plugin(None)  # type: ignore
        assert retrieved is dummy_plugin

    def test_plugin_functionality_after_registration(
        self, clean_plugin_registry, custom_dummy_plugin
    ):
        """Test that plugin functionality works correctly after registration."""
        plugin_name = "functional_test"
        register_plugin(plugin_name, custom_dummy_plugin)

        retrieved_plugin = get_plugin(plugin_name)

        # Test plugin methods work as expected
        assert retrieved_plugin.get_country_info("test") is not None
        assert retrieved_plugin.get_country_info("unknown") is None
        assert len(retrieved_plugin.get_supported_countries()) == 1
        assert len(retrieved_plugin.get_supported_regions()) == 1
        assert retrieved_plugin.convert_country_name("test country", "ISO2") == "TC"
        assert retrieved_plugin.get_flag("test country") == "🏁"
        assert retrieved_plugin.reverse_lookup("🏁") == "Test Country"

    def test_massive_plugin_registration_and_cleanup(self, clean_plugin_registry):
        """Test registering and unregistering a very large number of plugins."""
        num_plugins = 1000
        plugin_names = [f"massive_test_{i}" for i in range(num_plugins)]

        # Register all plugins
        for name in plugin_names:
            register_plugin(name, DummyPlugin(name))

        assert len(get_registered_plugins()) == num_plugins

        # Unregister all plugins
        for name in plugin_names:
            unregister_plugin(name)

        assert len(get_registered_plugins()) == 0

        # Verify none can be retrieved
        for name in plugin_names:
            with pytest.raises(PluginError):
                get_plugin(name)
