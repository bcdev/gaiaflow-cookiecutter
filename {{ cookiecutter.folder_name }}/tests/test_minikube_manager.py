import subprocess
import unittest
from pathlib import Path
from unittest.mock import ANY, mock_open, patch, call

import pytest
from minikube_manager import MinikubeManager, main


@pytest.mark.gaiaflow
class TestMinikubeManager(unittest.TestCase):

    def setUp(self):
        self.manager = MinikubeManager()

    @patch.object(MinikubeManager, "start_minikube")
    def test_init_with_start(self, mock_start):
        MinikubeManager(start=True)
        mock_start.assert_called_once()

    @patch.object(MinikubeManager, "stop_minikube")
    def test_init_with_stop(self, mock_stop):
        MinikubeManager(stop=True)
        mock_stop.assert_called_once()

    @patch.object(MinikubeManager, "start_minikube")
    @patch.object(MinikubeManager, "stop_minikube")
    def test_init_with_restart(self, mock_stop, mock_start):
        MinikubeManager(restart=True)
        mock_stop.assert_called_once()
        mock_start.assert_called_once()

    @patch.object(MinikubeManager, "build_docker_image")
    def test_init_with_build_only(self, mock_build):
        MinikubeManager(build_only=True)
        mock_build.assert_called_once()

    @patch.object(MinikubeManager, "create_kube_config_inline")
    def test_init_with_create_config_only(self, mock_cfg):
        MinikubeManager(create_config_only=True)
        mock_cfg.assert_called_once()

    @patch.object(MinikubeManager, "error")
    def test_run_with_exception_calls_error(self, mock_error):
        with patch("subprocess.call", side_effect=subprocess.CalledProcessError(1, ["fake"])):
            self.manager.run(["fake"], "Failed!")
            mock_error.assert_called_once_with("Failed!")

    def test_error_calls_sys_exit(self):
        with self.assertRaises(SystemExit) as cm:
            self.manager.error("fail msg")
        self.assertEqual(cm.exception.code, 1)

    @patch("sys.argv", ["minikube_manager.py", "--start"])
    @patch.object(MinikubeManager, "__init__", return_value=None)
    def test_main_with_start_flag(self, mock_init):
        main()
        mock_init.assert_called_once()
        self.assertTrue(mock_init.call_args.kwargs["start"])

    @patch("sys.argv", ["minikube_manager.py", "--build-only"])
    @patch.object(MinikubeManager, "__init__", return_value=None)
    def test_main_with_build_only_flag(self, mock_init):
        main()
        mock_init.assert_called_once()
        self.assertTrue(mock_init.call_args.kwargs["build_only"])

    @patch('subprocess.call')
    def test_run_success(self, mock_call):
        manager = MinikubeManager()
        mock_call.return_value = 0
        manager.run(["echo", "hello"], "Error executing command")
        mock_call.assert_called_with(["echo", "hello"], env=None)

    @patch('subprocess.call')
    def test_run_error(self, mock_call):
        manager = MinikubeManager()
        mock_call.side_effect = subprocess.CalledProcessError(1, "echo")
        with self.assertRaises(SystemExit):
            manager.run(["echo", "hello"], "Error executing command")

    @patch('subprocess.call')
    @patch('subprocess.run')
    def test_start(self, mock_subprocess_run, mock_call):
        manager = MinikubeManager()

        mock_call.return_value = None
        mock_subprocess_run.return_value.returncode = 0

        with patch.object(manager, 'start_minikube') as mock_start_minikube, \
                patch.object(manager, 'build_docker_image') as mock_build_docker_image, \
                patch.object(manager, 'create_kube_config_inline') as mock_create_kube_config_inline, \
                patch.object(manager, 'create_secrets') as mock_create_secrets:
            manager.start()

            mock_start_minikube.assert_called_once()
            mock_build_docker_image.assert_called_once()
            mock_create_kube_config_inline.assert_called_once()
            mock_create_secrets.assert_called_once_with(
                secret_name="my-minio-creds",
                secret_data={
                    "AWS_ACCESS_KEY_ID": "minio",
                    "AWS_SECRET_ACCESS_KEY": "minio123",
                }
            )

    @patch('subprocess.run')
    def test_start_minikube_already_running(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = b"Running"
        manager = MinikubeManager()
        with patch.object(manager, 'run') as mock_run:
            manager.start_minikube()
            mock_run.assert_not_called()

    @patch('subprocess.run')
    def test_start_minikube_not_running(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = b"Minikube cluster 'airflow' is stopped"
        manager = MinikubeManager()
        with patch.object(manager, 'run') as mock_run:
            manager.start_minikube()
            mock_run.assert_called_with(
                [
                    "minikube", "start", "--profile", manager.minikube_profile,
                    "--driver=docker", "--cpus=4", "--memory=4g"
                ],
                "Error starting minikube profile [airflow]"
            )

    @patch('subprocess.call')
    def test_stop_minikube(self, mock_call):
        manager = MinikubeManager()
        manager.stop_minikube()
        call_args_list = mock_call.call_args_list
        print(call_args_list)
        self.assertEqual(
            call_args_list[0],
            call(['minikube', 'stop', '--profile', 'airflow'], env=None)
                         )
        self.assertEqual(
            call_args_list[1],
            call(["minikube", "delete", "--profile", "airflow"], env=None),
        )

    @patch('subprocess.run')
    @patch('subprocess.call')
    def test_build_docker_image(self, mock_call, mock_subprocess_run):
        manager = MinikubeManager()
        mock_subprocess_run.return_value.stdout = b"export DOCKER_TLS_VERIFY=\"1\"\nexport DOCKER_HOST=\"tcp://127.0.0.1:2376\""
        manager.build_docker_image()
        mock_call.assert_called_with(
            ["docker", "build", "-t", manager.docker_image_name, "."],
            env=ANY
        )

    @patch('subprocess.call')
    @patch('subprocess.check_output')
    def test_create_kube_config_inline(self, mock_check_output, mock_call):
        manager = MinikubeManager()
        mock_check_output.return_value = b"minikube kubeconfig"
        with patch('pathlib.Path.home', return_value=Path("C:/Users/test")):
            with patch('builtins.open', mock_open(read_data='{"dummy config"}')):
                manager.create_kube_config_inline()
        mock_call.assert_called_with(
            [
                "minikube", "kubectl", "--", "config", "view", "--flatten", "--minify", "--raw"
            ],
            stdout=ANY
        )
