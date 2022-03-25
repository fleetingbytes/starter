# Contributing to starter

If you want to contribute, let's get in touch.

This document currently serves mainly as my personal guide of how to publish on PyPI.

## Workflow for manual deployment on IAV PyPI

* create virtual environment `python -m venv /path/to/venv`
* activate venv
* python -m pip install --upgrade pip
* pip install twine
* pip install wheel
* python setup.py sdist bdist_wheel
* ls dist
* make sure you have the TestPyPI and PyPI repository URLs in your ~/.pypirc
* make sure you have the path to your certificate bundle in your ~/.pypirc

```.pypirc
[distutils]
index-servers = 
	care
	testpypi
	pypi
cert = /path/to/your/certificaaate/bundle

[care]
repository = <YOUR_GITLAB_PYPI_URL>.../api/v4/projects/<project_id>/packages/pypi
username = gitlab+deploy-token-451
password = <YOUR_TOKEN_PASSWORD>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <YOUR_TOKEN_PASSWORD>

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = <YOUR_TOKEN_PASSWORD>
```

The IAV's PyPI registry is saved named `care` in the `pypirc`.
* `python -m twine upload --repository care dist/*`

Test if the package can be installed via pip.
* check if your pip.ini has proxies and certificates, e.g.

See `README.md` for the proper pip setup.
