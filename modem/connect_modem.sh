SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

while [ 1 ]
do
	$SCRIPT_DIR/../SIM8200_for_RPI/Goonline/simcom-cm
	sleep 3
done
