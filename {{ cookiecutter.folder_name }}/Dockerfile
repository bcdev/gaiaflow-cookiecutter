FROM  mambaorg/micromamba:latest

WORKDIR /app

COPY environment.yml .

RUN micromamba install -f environment.yml -n base

ENV PATH=/opt/conda/bin:$PATH

COPY {{ cookiecutter.package_name }} ./cookiecutter.package_name
COPY runner.py .

ENTRYPOINT ["python", "-m", "{{ cookiecutter.package_name }}.runner"]
