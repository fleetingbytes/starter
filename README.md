# starter

Use starter to kick-start your python project

## Dependencies

* [argcomplete][argcomplete] (argument completion)
* [loguru][loguru] (logging)
* [tomli][tomli] (to parse the `toml` configuraton file)
* [re_patterns][re_patterns] (for easy construction of regular expressions)

## Usage

## Installation

### Pip

```
pip install starter
```

To install starter with `pip` you first have to properly [setup pip](#pip-setup).

### Argument Completion
starter uses the python library [argcomplete][argcomplete] for argument completion. Argument completion in Windows PowerShell uses a wrapper script which is provided in this repository as `starter.complete.ps1`. Just source it (with the source or dot operator).

```
. .\starter.complete.ps1
```

Linux users please follow argcomplete's documentation to create and register the completions for your shell. 

### Pip setup

Your pip configuration is stored in your user folder under `\AppData\Roaming\pip\pip.ini` (hidden), linux users will find it [elsewhere][linuxpip]]). If the folder or file does not exist, create it. It content should look like this:

```
[global]
proxy = <YOUR_PROXY>
trusted-host = <YOUR_PYPI_REGISTRY>
               pypi.org
               test.pypi.org
               pypi.python.org
               files.pythonhosted.org
			   test-files.pythonhosted.org
extra-index-url = https://__token__:<***YOUR_ACCESS_TOKEN***>@<YOUR_PYPI_REGISTRY>
cert = ~/path/to/your/cert/bundle
```

Note by this you defined the necessary settings to:
* go through your proxy
* trust the PyPI registry server (that's where pip will find the `starter` package)
* pass your personal access token to access the package registry (replace `<***YOUR_ACCESS_TOKEN***>` with your actual access token)
* provide the URL for the PyPI registry
* provide valid path to the current certificates

Once set up, upgrade pip to the latest version (`python -m pip install --upgrade pip`).

### Developer's Installation

You can clone the repository and install it with `pip install -e /path/to/local/repository`.


[argcomplete]: https://pypi.org/project/argcomplete/
[linuxpip]: https://pip.pypa.io/en/stable/topics/configuration/#location
[loguru]: https://pypi.org/project/loguru/
[tomli]: https://pypi.org/project/tomli/
[re_patterns]: https://pypi.org/project/re-patterns/
