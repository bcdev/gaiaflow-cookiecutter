import re
import sys

project_name = "{{ cookiecutter.project_name }}"
project_description = "{{ cookiecutter.project_description }}"
author_name = "{{ cookiecutter.author_name }}"
author_email = "{{ cookiecutter.author_email }}"
show_examples = "{{ cookiecutter.show_examples }}"
package_name = "{{ cookiecutter.package_name }}"


if not project_name.strip():
    sys.stderr.write("ERROR: project_name cannot be empty.\n")
    sys.exit(1)

if show_examples not in ["yes", "no"]:
    sys.stderr.write("ERROR: show_examples must be 'yes' or 'no'.\n")
    sys.exit(1)


if not re.match(r"^[a-z_]+$", package_name):
    sys.stderr.write(
        "ERROR: package_name must contain only lowercase letters and underscores.\n"
    )
    sys.exit(1)

print("All inputs validated successfully!")
