import unittest
from unittest.mock import patch
import os

from mlops_manager import MlopsManager


class TestMlopsManager(unittest.TestCase):
    def setUp(self):
        self.manager = MlopsManager(
            cache=False, jupyter_port=8985, delete_volume=False, docker_build=False
        )
        self.test_dir = "temp_logs"
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_create_directory_real(self):
        self.manager.create_directory(self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))

    @patch("os.makedirs")
    @patch("os.chmod")
    def test_create_directory_new(self, mock_chmod, mock_makedirs):
        self.manager.create_directory(self.test_dir)
        mock_makedirs.assert_called_once_with(self.test_dir, exist_ok=True)
        mock_chmod.assert_called_once_with(self.test_dir, 0o777)

    @patch("os.chmod")
    def test_create_directory_exists(self, mock_chmod):
        self.manager.create_directory(self.test_dir)
        mock_chmod.assert_called_once_with(self.test_dir, 0o777)

    def test_handle_error_exits(self):
        with self.assertRaises(SystemExit):
            self.manager.handle_error("Test error")

    @patch("socket.socket.connect_ex", return_value=0)
    def test_check_port_in_use(self, mock_connect_ex):
        with self.assertRaises(SystemExit):
            self.manager.check_port()

    def test_handle_error_real(self):
        with self.assertRaises(SystemExit):
            self.manager.handle_error("Something failed")

    @patch("subprocess.Popen")
    @patch("subprocess.check_call")
    @patch.object(MlopsManager, "check_port")
    @patch.object(MlopsManager, "create_directory")
    @patch("signal.signal")
    @patch("signal.pause", side_effect=KeyboardInterrupt)
    def test_cleanup_no_volume(
        self,
        mock_pause,
        mock_signal,
        mock_create_dir,
        mock_check_port,
        mock_check_call,
        mock_popen,
    ):
        self.manager.delete_volume = False
        try:
            self.manager.start()
        except KeyboardInterrupt:
            pass
        self.manager.cleanup()
        mock_check_call.assert_any_call(["docker", "compose", "down"])

    @patch("subprocess.Popen")
    @patch("subprocess.check_call")
    @patch.object(MlopsManager, "check_port")
    @patch.object(MlopsManager, "create_directory")
    @patch("signal.signal")
    @patch("signal.pause", side_effect=KeyboardInterrupt)
    def test_cleanup_with_volume(
        self,
        mock_pause,
        mock_signal,
        mock_create_dir,
        mock_check_port,
        mock_check_call,
        mock_popen,
    ):
        self.manager.docker_build = False
        try:
            self.manager.start()
        except KeyboardInterrupt:
            pass
        self.manager.delete_volume = True
        self.manager.cleanup()
        mock_check_call.assert_any_call(["docker", "compose", "down", "-v"])

    @patch("subprocess.Popen")
    @patch("subprocess.check_call")
    @patch.object(MlopsManager, "check_port")
    @patch.object(MlopsManager, "create_directory")
    @patch("signal.signal")
    @patch("signal.pause", side_effect=KeyboardInterrupt)
    def test_start_without_build(
        self,
        mock_pause,
        mock_signal,
        mock_create_dir,
        mock_check_port,
        mock_check_call,
        mock_popen,
    ):
        self.manager.docker_build = False
        try:
            self.manager.start()
        except KeyboardInterrupt:
            pass
        mock_check_call.assert_called_with(["docker", "compose", "up", "-d"])
        mock_popen.assert_called_once()
        self.assertTrue(mock_signal.called)
        self.manager.cleanup()

    @patch("subprocess.Popen")
    @patch("subprocess.check_call")
    @patch.object(MlopsManager, "check_port")
    @patch.object(MlopsManager, "create_directory")
    @patch("signal.signal")
    @patch("signal.pause", side_effect=KeyboardInterrupt)
    def test_docker_build_with_cache(
        self,
        mock_pause,
        mock_signal,
        mock_create_dir,
        mock_check_port,
        mock_check_call,
        mock_popen,
    ):
        self.manager.docker_build = True
        self.manager.cache = True

        try:
            self.manager.start()
        except KeyboardInterrupt:
            pass
        mock_check_call.assert_any_call(["docker", "compose", "build"])
        mock_check_call.assert_any_call(["docker", "compose", "up", "-d"])
        self.manager.cleanup()

    @patch("subprocess.Popen")
    @patch("subprocess.check_call")
    @patch.object(MlopsManager, "check_port")
    @patch.object(MlopsManager, "create_directory")
    @patch("signal.signal")
    @patch("signal.pause", side_effect=KeyboardInterrupt)
    def test_docker_build_without_cache(
        self,
        mock_pause,
        mock_signal,
        mock_create_dir,
        mock_check_port,
        mock_check_call,
        mock_popen,
    ):
        self.manager.docker_build = True
        self.manager.cache = False
        try:
            self.manager.start()
        except KeyboardInterrupt:
            pass

        mock_check_call.assert_any_call(["docker", "compose", "build", "--no-cache"])
        mock_check_call.assert_any_call(["docker", "compose", "up", "-d"])
        self.manager.cleanup()
