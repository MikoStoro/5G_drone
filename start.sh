#start all components of the application
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR

echo "starting system..."
python -m venv $SCRIPT_DIR/drone-venv 
docker-compose up &  #prepare environment
sleep 5 #wait until mqtt server is online
python $SCRIPT_DIR/heart_module/heart.py #start central module

#start bt module
#start 5g driver

#the drone will run as long as the script is active

