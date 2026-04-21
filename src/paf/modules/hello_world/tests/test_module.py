"""
Unit tests for the HelloWorld class
"""
import unittest
import time
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from paf.communication import Protocol, Message, Module
from paf.modules.hello_world.module import HelloWorld


class TestHelloWorld(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = Protocol()

    def tearDown(self):
        """Clean up test fixtures"""
        # Send shutdown to all registered modules to stop their threads
        for module_name in self.protocol.get_registered_modules():
            try:
                self.protocol.send_action(module_name, "shutdown")
            except:
                pass
        # Wait a bit for threads to finish
        time.sleep(0.1)
        # Clean up any registered modules
        for module_name in self.protocol.get_registered_modules():
            try:
                self.protocol.unregister_module(module_name)
            except:
                pass
        del self.protocol

    def test_init(self):
        """Test HelloWorld initialization"""
        module = HelloWorld("test_hello_world", self.protocol, debug=0)
        self.assertEqual(module.address, "test_hello_world")
        self.assertEqual(module.protocol, self.protocol)
        self.assertEqual(module.debug, 0)
        self.assertIn("test_hello_world", self.protocol.registered_modules)
        self.assertTrue(module.thread.is_alive())
        self.assertFalse(module.background_task_running)

        # Clean up
        self.protocol.send_action("test_hello_world", "shutdown")
        module.thread.join(timeout=1.0)

    def test_init_with_debug(self):
        """Test HelloWorld initialization with debug enabled"""
        module = HelloWorld("test_hello_world_debug", self.protocol, debug=1)
        self.assertEqual(module.debug, 1)

        # Clean up
        self.protocol.send_action("test_hello_world_debug", "shutdown")
        module.thread.join(timeout=1.0)

    def test_handle_message_custom_action(self):
        """Test handle_message with custom_action command"""
        module = HelloWorld("test_hello_world", self.protocol, debug=0)
        msg = Message("test_hello_world", "custom_action", {"key": "value"})

        result = module.handle_message(msg)
        self.assertFalse(result)  # Should return False to continue running

        # Clean up
        self.protocol.send_action("test_hello_world", "shutdown")
        module.thread.join(timeout=1.0)

    def test_message_custom_action(self):
        """Test message_custom_action method directly"""
        module = HelloWorld("test_hello_world", self.protocol, debug=0)
        msg = Message("test_hello_world", "custom_action", {"data": "test"})

        result = module.message_custom_action(msg)
        self.assertFalse(result)  # Returns False

        # Clean up
        self.protocol.send_action("test_hello_world", "shutdown")
        module.thread.join(timeout=1.0)

    def test_handle_message_unknown(self):
        """Test handle_message with unknown command raises NotImplementedError"""
        module = HelloWorld("test_hello_world", self.protocol, debug=0)
        msg = Message("test_hello_world", "unknown_command")

        with self.assertRaises(NotImplementedError):
            module.handle_message(msg)

        # Clean up
        self.protocol.send_action("test_hello_world", "shutdown")
        module.thread.join(timeout=1.0)

    def test_background_task_running(self):
        """Test background task runs when enabled"""
        module = HelloWorld("test_hello_world", self.protocol, debug=0)

        # Start background task
        self.protocol.send_action("test_hello_world", "start")
        time.sleep(0.2)  # Give it time to start

        self.assertTrue(module.background_task_running)

        # Clean up
        self.protocol.send_action("test_hello_world", "shutdown")
