#!/bin/bash
#start all components of the application
export MAIN_DIR='/home/pi/5G_drone'
echo $MAIN_DIR



echo "starting system..."
VENV_PATH=$MAIN_DIR/drone-venv/bin/activate
echo $VENV_PATH
source $VENV_PATH

docker compose -f $MAIN_DIR/compose.yaml up &  #prepare environment
sleep 5 #wait until mqtt server is online
#python $MAIN_DIR/modem/modem_config.py #configure modem before use
echo 'MODEM CONFIGURED'
$MAIN_DIR/heart/run_heart.sh & #start central module
echo 'HEART STARTED'
$MAIN_DIR/modem/run_modem.sh & #start communication with the client
echo 'MODEM DAEMON RUNNING'
$MAIN_DIR/bluetooth/run_bluetooth.sh & #start communication with the client
echo 'BLUETOOTH DAEMON STARTED'

echo 'system is running' 

read -p "Press enter to stop" </dev/tty

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT


#the drone will run as long as the script is active

