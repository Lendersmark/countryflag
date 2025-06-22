"""
Plugin system for the countryflag package.

This package contains the plugin interface and plugin registry for extending
the functionality of the countryflag package.
"""

from typing import Any, Dict, List, Optional, Type

from countryflag.core.exceptions import PluginError
from countryflag.plugins.base import BasePlugin

# Registry of plugins
_plugin_registry: Dict[str, BasePlugin] = {}


def register_plugin(name: str, plugin: BasePlugin) -> None:
    """
    Register a plugin with the given name.

    Args:
        name: The name of the plugin.
        plugin: The plugin instance.

    Raises:
        PluginError: If a plugin with the same name is already registered.
    """
    if name in _plugin_registry:
        raise PluginError(f"Plugin '{name}' is already registered", name)

    _plugin_registry[name] = plugin


def get_plugin(name: str) -> BasePlugin:
    """
    Get a plugin by name.

    Args:
        name: The name of the plugin.

    Returns:
        BasePlugin: The plugin instance.

    Raises:
        PluginError: If the plugin is not registered.
    """
    if name not in _plugin_registry:
        raise PluginError(f"Plugin '{name}' is not registered", name)

    return _plugin_registry[name]


def get_registered_plugins() -> List[str]:
    """
    Get a list of registered plugin names.

    Returns:
        List[str]: A list of registered plugin names.
    """
    return list(_plugin_registry.keys())


def unregister_plugin(name: str) -> None:
    """
    Unregister a plugin.

    Args:
        name: The name of the plugin to unregister.

    Raises:
        PluginError: If the plugin is not registered.
    """
    if name not in _plugin_registry:
        raise PluginError(f"Plugin '{name}' is not registered", name)

    del _plugin_registry[name]


__all__ = [
    "BasePlugin",
    "register_plugin",
    "get_plugin",
    "get_registered_plugins",
    "unregister_plugin",
]
