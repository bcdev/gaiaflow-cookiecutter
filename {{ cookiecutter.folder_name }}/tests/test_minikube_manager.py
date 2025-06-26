import unittest
from unittest.mock import patch, call, mock_open
from minikube_manager import MinikubeManager


class TestMinikubeManager(unittest.TestCase):
    def setUp(self):
        self.manager = MinikubeManager(clean=False)

    @patch("shutil.which", return_value="/usr/local/bin/minikube")
    @patch("subprocess.run")
    @patch("subprocess.call")
    def test_cleanup_with_minikube_no_clean(self, mock_call, mock_run, mock_which):
        mock_run.return_value.returncode = 0
        self.manager.cleanup()
        self.assertIn(call(["minikube", "stop", "--profile", "airflow"]), mock_call.call_args_list)

    @patch("shutil.which", return_value=None)
    def test_cleanup_without_minikube_and_no_clean(self, mock_which):
        with self.assertRaises(SystemExit):
            self.manager.cleanup()

    @patch("os.path.exists", return_value=True)
    @patch("subprocess.check_call")
    def test_build_docker_image(self, mock_check_call, mock_exists):
        self.manager.build_docker_image()
        mock_check_call.assert_called_with(["docker", "build", "-t", self.manager.docker_image_name, "."])

    @patch("os.path.exists", return_value=False)
    def test_build_docker_image_no_dockerfile(self, mock_exists):
        with self.assertRaises(SystemExit):
            self.manager.build_docker_image()

    @patch.object(MinikubeManager, "log")
    @patch("subprocess.run", return_value=unittest.mock.Mock(returncode=0))
    def test_create_secrets_already_exists(self, mock_run, mock_log):
        self.manager.create_secrets(secret_name="my-minio-creds",
                    secret_data={
                        "AWS_ACCESS_KEY_ID": "minio",
                        "AWS_SECRET_ACCESS_KEY": "minio123"
                    })
        mock_log.assert_any_call("Secret [my-minio-creds] already exists. Skipping creation.")

    @patch.object(MinikubeManager, "log")
    @patch("subprocess.run", return_value=unittest.mock.Mock(returncode=1))
    @patch("subprocess.check_call")
    def test_create_secrets_new(self, mock_check_call, mock_run, mock_log):
        self.manager.create_secrets(secret_name="my-minio-creds",
                    secret_data={
                        "AWS_ACCESS_KEY_ID": "minio",
                        "AWS_SECRET_ACCESS_KEY": "minio123"
                    })
        mock_check_call.assert_called_with([
            "minikube", "kubectl", "-p", "airflow", "--",
            "create", "secret", "generic", "my-minio-creds",
            "--from-literal=AWS_ACCESS_KEY_ID=minio",
            "--from-literal=AWS_SECRET_ACCESS_KEY=minio123"
        ])
        print(mock_log.call_args)
        mock_log.assert_any_call("Creating secret [my-minio-creds]...")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("subprocess.check_call")
    @patch.object(MinikubeManager, "log")
    def test_create_kube_config_inline(
        self, mock_log, mock_subprocess, mock_exists, mock_file
    ):
        self.manager.create_kube_config_inline()
        test_filename = "kube_config_inline"
        mock_file.assert_called_once_with(test_filename, "w")
        mock_subprocess.assert_called_once_with(
            [
                "minikube",
                "kubectl",
                "--",
                "config",
                "view",
                "--flatten",
                "--minify",
                "--raw",
            ],
            stdout=mock_file(),
        )

        mock_log.assert_any_call("Creating kube config inline file...")
        mock_log.assert_any_call(
            f"Created kube config inline file {test_filename}"
        )
