# Edgerouter Memory and Storage Check
Get the Memory and Storage info from an Edgerouter via SSH to debug why the router may hang 
(e.g. if too many log entries get created)
## Installation
Make sure you have an influxdb (version 1) installed and configured your config/config_template.py saving the modified
template as config/config.py

## Usage

App was tested on Python 3.11
