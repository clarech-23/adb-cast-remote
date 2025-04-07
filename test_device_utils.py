import unittest
from unittest.mock import patch, MagicMock
import device_utils


class TestConnectToDevice(unittest.TestCase):

    def setUp(self):
        self.ip_address = "192.168.1.80"

    @patch("device_utils.subprocess.run")
    def test_connect_auth_failed(self, mock_subprocess_run):
        # First mock result: failed to authenticate
        mock_result_1 = MagicMock()
        mock_result_1.stdout = f"failed to authenticate to {self.ip_address}:5555\n"

        # Second mock result: already connected
        mock_result_2 = MagicMock()
        mock_result_2.stdout = f"already connected to {self.ip_address}:5555\n"

        # Return the two results in order
        mock_subprocess_run.side_effect = [mock_result_1, mock_result_2]

        # First call
        actual_result1 = device_utils.connect_to_device(self.ip_address)
        self.assertEqual(actual_result1, mock_result_1.stdout.strip())

        # Second call
        actual_result2 = device_utils.connect_to_device(self.ip_address)
        self.assertEqual(actual_result2, mock_result_2.stdout.strip())


    @patch("device_utils.subprocess.run")
    def test_connect_refused(self, mock_subprocess_run):
        """When the Chromecast does not have Developer Options enabled, what about if it's off?"""
        mock_result = MagicMock()
        mock_result.stdout = f"failed to connect to '{self.ip_address}:5555': Connection refused\n"
        mock_subprocess_run.return_value = mock_result

        actual_result = device_utils.connect_to_device(self.ip_address)
        self.assertEqual(actual_result, mock_result.stdout.strip())


    @patch("device_utils.subprocess.run")
    def test_connect_already_paired(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"already connected to {self.ip_address}:5555\n"
        mock_subprocess_run.return_value = mock_result

        actual_result = device_utils.connect_to_device(self.ip_address)
        self.assertEqual(actual_result, mock_result.stdout.strip())


    @patch("device_utils.subprocess.run")
    def test_connect_host_remembered(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = f"connected to {self.ip_address}:5555\n"
        mock_subprocess_run.return_value = mock_result

        actual_result = device_utils.connect_to_device(self.ip_address)
        self.assertEqual(actual_result, mock_result.stdout.strip())


if __name__ == '__main__':
    unittest.main()