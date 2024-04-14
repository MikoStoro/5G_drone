SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR

deactivate
rm -rf $SCRIPT_DIR/zigbee2mqtt-data
rm -rf $SCRIPT_DIR/drone-venv
rm $SCRIPT_DIR/drone.json

echo "teardown complete"
