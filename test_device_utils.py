import unittest
from unittest.mock import patch, MagicMock
import device_utils


class TestConnectToDevice(unittest.TestCase):

    @patch("device_utils.subprocess.run")
    def test_connect_auth_failed(self, mock_subprocess_run):
        ip_address = "192.168.1.1"
        # First mock result: failed to authenticate
        mock_result_1 = MagicMock()
        mock_result_1.stdout = f"failed to authenticate to {ip_address}:5555\n"

        # Second mock result: already connected
        mock_result_2 = MagicMock()
        mock_result_2.stdout = f"already connected to {ip_address}:5555\n"

        # Return the two results in order
        mock_subprocess_run.side_effect = [mock_result_1, mock_result_2]

        # First call
        result1 = device_utils.connect_to_device(ip_address)
        self.assertEqual(result1, f"failed to authenticate to {ip_address}:5555")

        # Second call
        result2 = device_utils.connect_to_device(ip_address)
        self.assertEqual(result2, f"already connected to {ip_address}:5555")

        # Case 1: connected to
        # Case 2: already connected to
        # Case 3: connection refused
        # Case 4: failed to authenticate

if __name__ == '__main__':
    unittest.main()