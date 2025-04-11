import unittest
from unittest.mock import patch, MagicMock
import auto_pair_to_cast_device as auto_pair


@patch("auto_pair_to_cast_device.utils.connect_to_cast_device")
@patch("auto_pair_to_cast_device.utils.get_device_status")
class TestAutoPairToCastDevice(unittest.TestCase):

    def setUp(self):
        self.ip_address = "192.168.1.80"

    @patch("builtins.print")
    def test_auto_pair_success(self, mock_print, mock_device_status, mock_connect):
        mock_connect.return_value = None
        mock_device_status.return_value = "device"

        auto_pair.auto_pair_to_device(self.ip_address)

        mock_connect.assert_called_once_with(self.ip_address, quiet_connect=True)
        mock_device_status.assert_called_once_with(self.ip_address)
        mock_print.assert_called_with(f"Connected to Google Cast-enabled device at {self.ip_address}!")

    @patch("auto_pair_to_cast_device.subprocess.run")
    @patch("builtins.print")
    def test_auto_pair_unauthorized(self, mock_print, mock_subprocess_run, mock_device_status,
                                    mock_connect):
        mock_connect.return_value = None
        mock_device_status.return_value = "unauthorized"
        mock_subprocess_run.return_value = None

        auto_pair.auto_pair_to_device(self.ip_address)

        mock_connect.assert_called_once_with(self.ip_address, quiet_connect=True)
        mock_device_status.assert_called_once_with(self.ip_address)
        mock_subprocess_run.assert_called_once()
        mock_print.assert_called_once_with(
            f"Connection to Google Cast-enabled device at {self.ip_address} is unauthorized. "
            f"Forgetting device...")

    @patch("builtins.print")
    def test_auto_pair_unsuccessful(self, mock_print, mock_device_status, mock_connect):
        mock_connect.return_value = None
        mock_device_status.return_value = "offline"

        auto_pair.auto_pair_to_device(self.ip_address)

        mock_connect.assert_called_once_with(self.ip_address, quiet_connect=True)
        mock_device_status.assert_called_once_with(self.ip_address)
        mock_print.assert_called_with("Unable to connect to Google Cast-enabled device.")

    def test_auto_pair_unknown_status(self, mock_device_status, mock_connect):
        mock_connect.return_value = None
        mock_device_status.return_value = "unknown status"

        with self.assertRaises(NotImplementedError) as context:
            auto_pair.auto_pair_to_device(self.ip_address)

        mock_connect.assert_called_once_with(self.ip_address, quiet_connect=True)
        mock_device_status.assert_called_once_with(self.ip_address)
        self.assertIn("Handling of unknown connection status", str(context.exception))