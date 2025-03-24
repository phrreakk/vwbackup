# vwbackup

vwbackup is a python application that backs up a Vaultwarden* user vault and/or Organizations.

\* Bitwarden vaults were **not tested** but should be compatible...YMMV

## Features

* vwbackup can take input from command line arguments, an .env file, or environment variables.

* vwbackup will automatically output files to a directory of your choosing with a folder structure containing /Year/Month/Day folders.  Example /output_folder/2025/02/24/email_passwords.enc

* vwbackup will automatically prepend user email to user vaults.  Organization names will be prepended to organization vaults.

* All backups (user and orgs) are encrypted with the user password given during runtime.

## Security Limitations

* Master user password is required for exporting a vault.

## Installation

### Docker container

For a truly platform independent solution, use the official docker image:

```docker pull ghcr.io/phrreakk/vwbackup:2025.1.3-vwbackup1```

The docker container runs as the `vwbackup` user with a UID of `3003`.

The docker tag is tied to the version of the underlying Bitwarden CLI.  In the tag above, the Bitwarden CLI version is 2025.1.3.  I am doing this so that if there are breaking changes in the Bitwarden CLI, you may stay at an older version of vwbackup and keep your backups working.  After the CLI version is a dash and then vwbackup1.  The vwbackup1 is the first update to the logic of the vmbackup tool.  

### Python runtime

* Bitwarden CLI ```2025.1.3``` at time of this writing
  * <https://github.com/bitwarden/clients/releases/tag/cli-v2025.1.3>

* Install python 3.x. (3.13.1 version this was written against)

* Git clone this repository to your system.

* Create a virtual environment to safely run this application
  
  * ```python -m venv .venv``` inside your folder

* Run ```pip install -r requirements.txt```

\* I am a Linux user.  If you run on Windows, YMMV but Python should function cross platform.  Please open an issue if this is not the case.

## Usage

```text
options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Full path to output folder (Defaults to /app/output for docker container)
  -s, --server SERVER  Server URL if using self hosted instance
  --email EMAIL        User email login
  --password PASSWORD  User password for login (fairly insecure)
  --orgs               Backup the organizations you have access to export
  --docker             Docker mode
  --debug              Debug output
```

* ```-o or --output```is used to direct the application where to store your encrypted output files.  This will default to ```/app/output``` for compatibility with the docker container run, but you may change it for Python script runs.  (Full paths are suggested but relative paths are accepted)

* ```-s or --server``` is used to change the location of the Vaultwarden instance if you are self-hosting the instance.  By default, the server is pointed at the default Bitwarden instance in the cloud.

* ```--email``` is used to define the email address of the user account.  It is better practice to store this value in an environment variable or .env file.  (see below)

* ```--password``` is used to define the password for the user account.  It is better practice to store this value in an environment variable or .env file.  (see below)

* ```--orgs``` is used if you are running this as a Python script and want to backup all of your Organizations as well.  Otherwise, user vaults are the only vaults that are exported from the application.

* ```--docker``` is used to run the application from a container.  The application output will be very verbose and expect environment variables to be set before running.

* ```--debug``` is used to print out very verbose data from the application.  Not all that useful, unless something has gone very wrong.

### .env file

```text
email="myname@emaildomain.org"
password="This1smiSup3rS3cu4ePassword!"
```

### Environment variables

| Variable | Required | Description | Example |
| --- | --- | --- | --- |
| BW_SERVER | No | Full URL to your instance Defaults to <https://bitwarden.com> | <https://myinstance.mydomain.org> |
| BW_EMAIL | Yes | Email address for the user | <me@mydomain.org> |
| BW_PASSWORD | Yes | User password to export the vault(s) | mYp@ssword |
| BW_ORG_BACKUP | No | Whether to backup Organizations as well |True or False |

## Contributions

I am open to suggestions, contributions, requests, and PRs.

I created this application in my spare time.  I will do my best to update it as needed.  Please open an issue and I will do my best to resolve it in time.  
