SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

while [ 1 ]
do
	python $SCRIPT_DIR/mqtt_daemon.py
	sleep 2
done


