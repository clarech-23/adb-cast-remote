import unittest
from unittest.mock import patch, MagicMock
import device_utils

@patch("device_utils.subprocess.run")
class TestGetIpAddress(unittest.TestCase):

    def test_one_ip_address_found(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = "192.168.1.80\n"
        mock_subprocess_run.return_value = mock_result

        actual_result = device_utils.find_device_ip_address()
        self.assertEqual(actual_result, "192.168.1.80")

    def test_no_ip_address_found(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_subprocess_run.return_value = mock_result

        with self.assertRaises(SystemExit) as context:
            device_utils.find_device_ip_address()

        self.assertEqual(context.exception.code, 0)

    def multiple_ip_addresses_found(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = "192.168.1.70\n192.168.1.80\n192.168.1.90\n"
        mock_subprocess_run.return_value = mock_result

        with self.assertRaises(NotImplementedError) as context:
            device_utils.find_device_ip_address()

        self.assertIn("Handling of multiple Cast-enabled devices", str(context.exception))


@patch("device_utils.subprocess.run")
class TestConnectToDeviceSuccessful(unittest.TestCase):

    def setUp(self):
        self.ip_address = "192.168.1.80"

    @patch("device_utils.get_device_status")
    def test_connect_auth_failed(self, mock_device_status, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"failed to authenticate to {self.ip_address}:5555\n"
        mock_subprocess_run.return_value = mock_result
        mock_device_status.return_value = None

        actual_result = device_utils.connect_to_cast_device(self.ip_address)
        self.assertEqual(actual_result, False)

    @patch("device_utils.get_device_status")
    def test_connect_already_paired(self, mock_device_status, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"already connected to {self.ip_address}:5555\n"
        mock_subprocess_run.return_value = mock_result
        mock_device_status.return_value = "device"

        actual_result = device_utils.connect_to_cast_device(self.ip_address)
        self.assertEqual(actual_result, True)

    @patch("device_utils.get_device_status")
    def test_connect_unauthorized_pair(self, mock_device_status, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"already connected to {self.ip_address}:5555\n"
        mock_subprocess_run.return_value = mock_result
        mock_device_status.return_value = "unauthorized"

        actual_result = device_utils.connect_to_cast_device(self.ip_address)
        self.assertEqual(actual_result, False)

    @patch("device_utils.get_device_status")
    def test_connect_host_remembered(self, mock_device_status, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"connected to {self.ip_address}:5555\n"
        mock_subprocess_run.return_value = mock_result
        mock_device_status.return_value = None

        actual_result = device_utils.connect_to_cast_device(self.ip_address)
        self.assertEqual(actual_result, True)

    def test_device_status_offline(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = "offline"
        mock_subprocess_run.return_value = mock_result

        actual_result = device_utils.get_device_status(self.ip_address)
        self.assertEqual(actual_result, mock_result.stdout)

    def test_device_status_unauthorized(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = "unauthorized"
        mock_subprocess_run.return_value = mock_result

        actual_result = device_utils.get_device_status(self.ip_address)
        self.assertEqual(actual_result, mock_result.stdout)

    def test_device_status_connected(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = "device"
        mock_subprocess_run.return_value = mock_result

        actual_result = device_utils.get_device_status(self.ip_address)
        self.assertEqual(actual_result, mock_result.stdout)

    @patch("builtins.print")
    def test_disconnect_from_device_success(self, mock_print, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"disconnected {self.ip_address}"
        mock_subprocess_run.return_value = mock_result

        device_utils.disconnect_from_device(self.ip_address)
        mock_print.assert_called_with(f"Disconnected from device {self.ip_address}")


@patch("device_utils.subprocess.run")
class TestConnectToDeviceFailed(unittest.TestCase):

    def setUp(self):
        self.ip_address = "192.168.1.80"

    def test_connect_invalid_ip_address(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"failed to connect to '{self.ip_address}:5555': No route to host\n"
        mock_subprocess_run.return_value = mock_result

        with self.assertRaises(RuntimeError) as context:
            device_utils.connect_to_cast_device(self.ip_address)

        self.assertIn("Check if device is connected to the local network", str(context.exception))

    def test_connect_invalid_input(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"failed to resolve host '{self.ip_address}': Name or service not known"
        mock_subprocess_run.return_value = mock_result

        with self.assertRaises(RuntimeError) as context:
            device_utils.connect_to_cast_device(self.ip_address)

        self.assertIn("is an invalid IP address", str(context.exception))

    def test_unknown_connection_outcome(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = "unknown"
        mock_subprocess_run.return_value = mock_result

        with self.assertRaises(RuntimeError) as context:
            device_utils.connect_to_cast_device(self.ip_address)

        self.assertIn("Unexpected connection outcome", str(context.exception))

    def test_connect_refused(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"failed to connect to '{self.ip_address}:5555': Connection refused"
        mock_subprocess_run.return_value = mock_result

        with self.assertRaises(RuntimeError) as context:
            device_utils.connect_to_cast_device(self.ip_address)

        self.assertIn("Check if Developer Options and USB Debugging", str(context.exception))

    def test_device_status_not_found(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_subprocess_run.return_value = mock_result

        with self.assertRaises(RuntimeError) as context:
            device_utils.get_device_status(self.ip_address)

        self.assertIn("No device with IP address", str(context.exception))

    def test_disconnect_from_device_fail(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"error: no such device '{self.ip_address}':5555"
        mock_subprocess_run.return_value = mock_result

        with self.assertRaises(RuntimeError) as context:
            device_utils.disconnect_from_device(self.ip_address)

        self.assertIn("No such device", str(context.exception))


if __name__ == '__main__':
    unittest.main()