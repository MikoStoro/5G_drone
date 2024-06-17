SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

while [ 1 ]
do
	python $MAIN_DIR/heart/heart.py
	sleep 2
done
