"""Tests for mcp2-toolbox CLI functionality."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from mcp2_toolbox.cli import (
    Device,
    MCP2ToolboxError,
    ConfigurationError,
    DeviceError,
    load_config,
    discover,
    cmd_list,
    cmd_ui,
    cmd_new,
    cmd_watch,
    cmd_run,
    cmd_hook_install,
    cmd_config,
    create_parser,
    main
)


class TestDevice:
    """Test Device dataclass."""
    
    def test_device_creation(self):
        """Test device creation with name and IP."""
        device = Device(name="test-device", ip="192.168.1.100")
        assert device.name == "test-device"
        assert device.ip == "192.168.1.100"


class TestExceptions:
    """Test custom exceptions."""
    
    def test_mcp2_toolbox_error(self):
        """Test base exception."""
        with pytest.raises(MCP2ToolboxError):
            raise MCP2ToolboxError("Test error")
    
    def test_configuration_error(self):
        """Test configuration exception."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config error")
    
    def test_device_error(self):
        """Test device exception."""
        with pytest.raises(DeviceError):
            raise DeviceError("Device error")


class TestLoadConfig:
    """Test configuration loading."""
    
    def test_load_config_no_file(self):
        """Test loading config when file doesn't exist."""
        with patch('os.path.expanduser', return_value='/nonexistent/path'):
            config = load_config()
            assert config == {}
    
    @patch('mcp2_toolbox.cli.yaml')
    def test_load_config_yaml_error(self, mock_yaml):
        """Test loading config with YAML error."""
        mock_yaml.safe_load.side_effect = Exception("YAML error")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("invalid: yaml: content")
            temp_path = f.name
        
        try:
            with patch('os.path.expanduser', return_value=temp_path):
                with pytest.raises(ConfigurationError):
                    load_config()
        finally:
            os.unlink(temp_path)
    
    @patch('mcp2_toolbox.cli.yaml')
    def test_load_config_success(self, mock_yaml):
        """Test successful config loading."""
        mock_yaml.safe_load.return_value = {"test": "value"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test: value")
            temp_path = f.name
        
        try:
            with patch('os.path.expanduser', return_value=temp_path):
                config = load_config()
                assert config == {"test": "value"}
        finally:
            os.unlink(temp_path)


class TestDiscover:
    """Test device discovery."""
    
    @patch('mcp2_toolbox.cli.Zeroconf', None)
    def test_discover_no_zeroconf(self):
        """Test discovery when Zeroconf is not available."""
        devices = discover()
        assert devices == []
    
    @patch('mcp2_toolbox.cli.Zeroconf')
    @patch('mcp2_toolbox.cli.ServiceBrowser')
    def test_discover_success(self, mock_browser, mock_zeroconf):
        """Test successful device discovery."""
        # Mock Zeroconf instance
        mock_zc_instance = MagicMock()
        mock_zeroconf.return_value = mock_zc_instance
        
        # Mock service info
        mock_info = MagicMock()
        mock_info.addresses = [[192, 168, 1, 100]]
        mock_zc_instance.get_service_info.return_value = mock_info
        
        devices = discover(timeout_sec=0.1)
        
        # Verify Zeroconf was used
        mock_zeroconf.assert_called_once()
        mock_browser.assert_called_once()
        mock_zc_instance.close.assert_called_once()


class TestCommands:
    """Test command functions."""
    
    @patch('mcp2_toolbox.cli.discover')
    def test_cmd_list(self, mock_discover):
        """Test list command."""
        mock_discover.return_value = [
            Device(name="device1", ip="192.168.1.100"),
            Device(name="device2", ip="192.168.1.101")
        ]
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            cmd_list()
            
            # Verify devices were printed
            assert mock_print.call_count >= 2
    
    @patch('mcp2_toolbox.cli.discover')
    def test_cmd_list_no_devices(self, mock_discover):
        """Test list command with no devices."""
        mock_discover.return_value = []
        
        with patch('builtins.print') as mock_print:
            cmd_list()
            
            # Should print "No MCP2 devices found"
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("No MCP2 devices found" in call for call in calls)


class TestParser:
    """Test argument parser."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None
        
        # Test help
        with pytest.raises(SystemExit):
            parser.parse_args(['--help'])
    
    def test_parser_commands(self):
        """Test parser with different commands."""
        parser = create_parser()
        
        # Test list command
        args = parser.parse_args(['list'])
        assert args.command == 'list'
        
        # Test new command
        args = parser.parse_args(['new', 'test-project'])
        assert args.command == 'new'
        assert args.name == 'test-project'
        
        # Test watch command with options
        args = parser.parse_args(['watch', '--project', './test', '--elf', './test.elf'])
        assert args.command == 'watch'
        assert args.project == './test'
        assert args.elf == './test.elf'


class TestMain:
    """Test main function."""
    
    def test_main_no_command(self):
        """Test main with no command."""
        with patch('sys.argv', ['mcp2-toolbox']):
            with patch('mcp2_toolbox.cli.create_parser') as mock_parser:
                mock_parser_instance = MagicMock()
                mock_parser_instance.parse_args.return_value = MagicMock(command=None)
                mock_parser.return_value = mock_parser_instance
                
                result = main()
                assert result == 1
    
    def test_main_keyboard_interrupt(self):
        """Test main with keyboard interrupt."""
        with patch('sys.argv', ['mcp2-toolbox', 'list']):
            with patch('mcp2_toolbox.cli.create_parser') as mock_parser:
                mock_parser_instance = MagicMock()
                mock_parser_instance.parse_args.side_effect = KeyboardInterrupt()
                mock_parser.return_value = mock_parser_instance
                
                result = main()
                assert result == 130
    
    def test_main_mcp2_error(self):
        """Test main with MCP2ToolboxError."""
        with patch('sys.argv', ['mcp2-toolbox', 'list']):
            with patch('mcp2_toolbox.cli.create_parser') as mock_parser:
                mock_parser_instance = MagicMock()
                mock_parser_instance.parse_args.side_effect = MCP2ToolboxError("Test error")
                mock_parser.return_value = mock_parser_instance
                
                result = main()
                assert result == 1


if __name__ == '__main__':
    pytest.main([__file__])
