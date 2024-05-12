#start all components of the application
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR

echo "starting system..."
python -m venv $SCRIPT_DIR/drone-venv 
docker-compose up &  #prepare environment
sleep 5 #wait until mqtt server is online
python $SCRIPT_DIR/heart_module/heart.py #start central module
python $SCRIPT_DIR/modem/modem_config.py #configure modem before use
python $SCRIPT_DIR/modem/mqtt_daemon.py #start communication with the client

#start bt module

#the drone will run as long as the script is active

