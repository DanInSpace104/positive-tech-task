# positive-tech-task

## Install
```sh

# create and activate env
python3.11 -m venv env
source env/bin/activate

# install requirements
python -m pip install -r requirements.txt

# initialize default sqlite database
python src/cli.py crawler init-database
```

## Run
After activating the environment:
* `python src/cli.py --help` - list of avaliable commands
    * `python src/cli.py server run` - start fastapi server

## Simple Testing
* `python src/cli.py crawler request-create-task <username>` - will print created task id
* `python src/cli.py crawler request-get-task <task-id>` - will print task result

**WARNING**: `crawler` cli module was created for testing purposes and has hardcoded values!

## Configuration
* `src/config.py` - Global configuration
* `src/codehub_crawler/config.py` - CodeHubCrawler specific configuration
* `src/codehub_crawler/context.py` - CodeHubCrawler context initialization
    * For example you can set self.codehub_storage = EmulatorCodeHubStorage(settings) to use local code repository hub emulator.
    To start it you can run `python gh-emulator/main.py`

In order to request data from github api you need to set GH_API_TOKEN environment variable.
[How to create GitHub Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
