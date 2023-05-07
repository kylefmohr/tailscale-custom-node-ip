#### Customize the IP of nodes in your Tailscale tailnet (within 100.64.0.0/10 subnet)
 - make sure the requests library is installed
 - fill out the 5 variables in all caps at the beginning of `main.py` (instructions in comments)
 - run `python3 main.py` and be patient - it is set to regenerate the IP once every three seconds or so
 - if you remove the `time.sleep`, you'll exceed their api limits and have to restart the script/get temporarily banned from using the api
 - script assumes you have the tailscale cli installed
 - use at your own risk