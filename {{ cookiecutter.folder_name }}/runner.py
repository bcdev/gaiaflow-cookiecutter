import importlib
import json
import os

def main():
    func_path = os.environ.get("FUNC_PATH", "")
    kwargs = json.loads(os.environ.get("FUNC_KWARGS", "{}"))

    if func_path:
        module_path, func_name = func_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)

        print(f"Running {func_path} with args: {kwargs}")
        result = func(**kwargs)
        print("Function result:", result)
        with open("/airflow/xcom/return.json", "w") as f:
            json.dump(result, f)

if __name__ == "__main__":
    main()
