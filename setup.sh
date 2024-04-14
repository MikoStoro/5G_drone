#this needs to be run every time the config is changed
#then you need to run this only once
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR

chmod +x $SCRIPT_DIR/start.sh
chmod +x $SCRIPT_DIR/teardown.sh

echo "running teardown..."
source $SCRIPT_DIR/teardown.sh


mkdir $SCRIPT_DIR/zigbee2mqtt-data
cp $SCRIPT_DIR/config-files/zigbee2mqtt_configuration.yaml $SCRIPT_DIR/zigbee2mqtt-data/configuration.yaml

python -m venv $SCRIPT_DIR/drone-venv #create venv for drone
source $SCRIPT_DIR/drone-venv/bin/activate
python -m pip install -r $SCRIPT_DIR/requirements.txt #install dependencies

echo 'setup complete'