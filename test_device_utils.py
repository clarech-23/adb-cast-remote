import unittest
from unittest.mock import patch, MagicMock
import device_utils


class TestConnectToDevice(unittest.TestCase):

    @patch("device_utils.subprocess.run")
    def test_connect_auth_failed(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.stdout = "failed to authenticate to 192.168.1.1:5555\n"
        mock_subprocess_run.return_value = mock_result

        actual_result = device_utils.connect_to_device("192.168.1.1")
        expected_result = "failed to authenticate to 192.168.1.1:5555"
        self.assertEqual(actual_result, expected_result)

        # Case 1: connected to
        # Case 2: already connected to
        # Case 3: connection refused
        # Case 4: failed to authenticate

if __name__ == '__main__':
    unittest.main()