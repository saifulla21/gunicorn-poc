# gunicorn-poc
standalone app which support async and long living websocket connections


Command to run the app in aync mode:
GUNICORN_CMD_ARGS="--bind=0.0.0.0:8080 --log-level info --workers=4" gunicorn -k gevent_pywsgi controller:app 

Command to run node.js client
node ws-client.js (Install all required packages)
