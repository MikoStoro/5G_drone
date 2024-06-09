#start all components of the application
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR



echo "starting system..."
source $SCRIPT_DIR/drone-venv/bin/activate

docker compose up &  #prepare environment
sleep 5 #wait until mqtt server is online
python $SCRIPT_DIR/modem/modem_config.py #configure modem before use
echo 'MODEM CONFIGURED'
$SCRIPT_DIR/heart_module/run_heart.sh & #start central module
echo 'HEART STARTED'
$SCRIPT_DIR/modem/run_modem.sh & #start communication with the client
echo 'MODEM DAEMON RUNNING'

echo 'system is running' 


read -p "Press enter to stop" </dev/tty

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

#start bt module

#the drone will run as long as the script is active

