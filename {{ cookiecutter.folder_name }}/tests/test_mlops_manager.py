import unittest
from unittest.mock import patch
import os
import shutil
import sys

from mlops_manager import main as mlops_main, MlopsManager


class TestMlopsManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "temp_logs"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

        self.manager = MlopsManager(
            action=None,
            service=None,
            cache=False,
            jupyter_port=8985,
            delete_volume=False,
            docker_build=False,
        )

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_init_start_calls_start(self):
        with patch.object(MlopsManager, "start") as mock_start:
            MlopsManager(action="start")
            mock_start.assert_called_once()

    def test_init_stop_calls_cleanup(self):
        with patch.object(MlopsManager, "cleanup") as mock_cleanup:
            MlopsManager(action="stop")
            mock_cleanup.assert_called_once()

    def test_init_restart_calls_cleanup_and_start(self):
        with patch.object(MlopsManager, "start") as mock_start, patch.object(MlopsManager, "cleanup") as mock_cleanup:
            MlopsManager(action="restart")
            mock_cleanup.assert_called_once()
            mock_start.assert_called_once()

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
        os.makedirs(self.test_dir, exist_ok=True)
        self.manager.create_directory(self.test_dir)
        mock_chmod.assert_called_once_with(self.test_dir, 0o777)

    def test_handle_error_exits(self):
        with self.assertRaises(SystemExit):
            self.manager.handle_error("Test error")

    @patch("socket.socket.connect_ex", return_value=0)
    def test_check_port_in_use(self, mock_connect_ex):
        with self.assertRaises(SystemExit):
            self.manager.check_port()

    @patch("psutil.process_iter")
    def test_stop_jupyter(self, mock_process_iter):
        mock_proc = unittest.mock.Mock()
        mock_proc.info = {
            "pid": 123,
            "name": "jupyter",
            "cmdline": ["python", "-m", "jupyter-lab"]
        }
        mock_process_iter.return_value = [mock_proc]
        self.manager.stop_jupyter()
        mock_proc.terminate.assert_called_once()

    def test_docker_services_for(self):
        self.assertEqual(
            MlopsManager.docker_services_for("airflow"),
            ["airflow-webserver", "airflow-scheduler", "airflow-init", "postgres-airflow"],
        )
        self.assertEqual(MlopsManager.docker_services_for("none"), [])

    @patch("subprocess.check_call")
    def test_docker_compose_action_all(self, mock_check_call):
        self.manager.docker_compose_action(["up", "-d"])
        mock_check_call.assert_called_once()

    @patch("subprocess.check_call")
    def test_docker_compose_action_with_service(self, mock_check_call):
        self.manager.service = "mlflow"
        self.manager.docker_compose_action(["up", "-d"], "mlflow")
        self.assertTrue(mock_check_call.called)

    def test_docker_compose_action_with_invalid_service(self):
        with self.assertRaises(SystemExit):
            self.manager.docker_compose_action(["up", "-d"], "unknown_service")

    @patch("subprocess.check_call")
    @patch("psutil.process_iter", return_value=[])
    def test_cleanup_jupyter(self, mock_iter, mock_check_call):
        manager = MlopsManager(
            action=None,
            service="jupyter",
            cache=False,
            jupyter_port=8985,
            delete_volume=False,
            docker_build=False,
        )
        manager.cleanup()
        self.assertTrue(mock_iter.called)
        mock_check_call.assert_not_called()

    @patch("subprocess.check_call")
    def test_cleanup_with_volume(self, mock_check_call):
        self.manager.service = "mlflow"
        self.manager.delete_volume = True
        self.manager.cleanup()
        mock_check_call.assert_called_with(
            ["docker", "compose", "down", "-v", "mlflow", 'postgres-mlflow', "minio", "minio_client"]
        )

    @patch("subprocess.check_call")
    def test_cleanup_without_volume(self, mock_check_call):
        self.manager.service = "mlflow"
        self.manager.delete_volume = False
        self.manager.cleanup()
        mock_check_call.assert_called_with(
            ["docker", "compose", "down", "mlflow", 'postgres-mlflow', "minio", "minio_client"]
        )

    @patch("subprocess.Popen")
    @patch("subprocess.check_call")
    @patch("socket.socket.connect_ex", return_value=1)
    def test_start_jupyter(self, mock_connect, mock_check_call, mock_popen):
        self.manager.service = "jupyter"
        self.manager.start()
        mock_popen.assert_called_once()

    @patch("subprocess.check_call")
    @patch("subprocess.Popen")
    def test_start_service_without_build(self, mock_popen, mock_check_call):
        self.manager.service = "mlflow"
        self.manager.docker_build = False
        self.manager.start()
        self.assertTrue(mock_check_call.called)
        mock_popen.assert_not_called()

    @patch("subprocess.check_call")
    def test_start_with_build_and_cache(self, mock_check_call):
        self.manager.docker_build = True
        self.manager.cache = True
        self.manager.service = "mlflow"
        self.manager.start()
        mock_check_call.assert_any_call(["docker", "compose", "build"])
        mock_check_call.assert_any_call(["docker", "compose", "up", "-d", "mlflow", "postgres-mlflow", "minio", "minio_client"])

    @patch("subprocess.check_call")
    def test_start_with_build_no_cache(self, mock_check_call):
        self.manager.docker_build = True
        self.manager.cache = False
        self.manager.service = "mlflow"
        self.manager.start()
        mock_check_call.assert_any_call(["docker", "compose", "build", "--no-cache"])
        mock_check_call.assert_any_call(["docker", "compose", "up", "-d", "mlflow", "postgres-mlflow", "minio", "minio_client"])

    @patch("sys.argv", ["mlops_manager.py", "--start"])
    @patch.object(MlopsManager, "__init__", return_value=None)
    def test_main_with_start_flag(self, mock_init):
        mlops_main()
        mock_init.assert_called_once()
        self.assertTrue(mock_init.call_args.kwargs["action"], "start")

    @patch("sys.argv", ["mlops_manager.py", "--stop"])
    @patch.object(MlopsManager, "__init__", return_value=None)
    def test_main_with_stop_flag(self, mock_init):
        mlops_main()
        mock_init.assert_called_once()
        self.assertTrue(mock_init.call_args.kwargs["action"], "stop")

    @patch("sys.argv", ["mlops_manager.py", "--restart"])
    @patch.object(MlopsManager, "__init__", return_value=None)
    def test_main_with_restart_flag(self, mock_init):
        mlops_main()
        mock_init.assert_called_once()
        self.assertTrue(mock_init.call_args.kwargs["action"], "restart")

    @patch("sys.argv", ["mlops_manager.py", "--start", "--service", "mlflow"])
    @patch.object(MlopsManager, "__init__", return_value=None)
    def test_main_with_service_argument(self, mock_init):
        mlops_main()
        mock_init.assert_called_once()
        self.assertEqual(mock_init.call_args.kwargs["service"], "mlflow")

    @patch("sys.argv", ["mlops_manager.py", "--start", "-j", "9999", "-v", "-c", "-b"])
    @patch.object(MlopsManager, "__init__", return_value=None)
    def test_main_with_all_args(self, mock_init):
        mlops_main()
        kwargs = mock_init.call_args.kwargs
        print(kwargs)
        self.assertTrue(kwargs["action"], "start")
        self.assertEqual(kwargs["jupyter_port"], 9999)
        self.assertTrue(kwargs["delete_volume"])
        self.assertTrue(kwargs["cache"])
        self.assertTrue(kwargs["docker_build"])
