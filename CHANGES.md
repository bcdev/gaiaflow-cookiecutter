## Changes in 0.1.1

### Enhancements

* Added `publish.yml` for publishing the package to PyPi for generated projects.
* Improved documentation in `MLOps.md`

### Fixes

* Fixed Github workflow bugs.
* Fixed issue with quotations in f-strings causing test failure.

## Changes in 0.1.0

### Enhancements

* **GaiaFlow Framework**: Introduced GaiaFlow, a local MLOps framework designed 
to streamline and standardize the structure of machine learning projects. 
* Key Features:
  * Standardized Project Structure: Ensures consistent project organization for 
  ML workflows.
  * Comprehensive Examples: End-to-end ML pipeline examples provided to 
  demonstrate the framework’s usage.
  * Initial Testing & CI Setup: Basic tests and continuous integration 
  pipelines included, with flexibility for users to expand.
  * Documentation: Detailed documentation outlining the framework’s components
  and how to use them effectively.
* Included Tools:
  * **Airflow**: For orchestration and workflow management.
  * **MLFlow**: For tracking experiments and managing the ML lifecycle.
  * **Jupyter** Lab: For interactive development and analysis.
  * **MinIO**: For object storage compatible with S3 APIs.
  * **Cookiecutter**: Used to generate the standardized project structure.