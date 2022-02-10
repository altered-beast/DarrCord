# DarrCord 
## installation

- run `pipenv install` to install the dependencies 
- create a `config.ini` file and fill in the values as specified in the config.example.ini
- and finally run bot.py with python
## usage
`request {series}` requests a series be added to sonarr . the admin designated in `config.ini` will recieve a messagevalerting them to your request and can then accept or deny the request

`deny {request}` denies the specified request. if called without specifiying a request lists the current requests instead

`accept {request}` accepts the specified request then adds it to sonarr and attempts to download it(this can take a while) . if called without specifiying a request lists the current requests instead
## Disclaimer
this software is not to be used for piracy and i do not support piracy. please research your local laws and ensure your usage is legal.
