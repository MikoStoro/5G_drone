
ADDR=$1
echo $ADDR

if [ -z "$ADDR" ]; then
    ADDR="8.8.8.8"
fi

ping -c 1 -w 1 $ADDR > /dev/null

if [ $? -eq 0 ]; then
    echo "Online"
else
    echo "Offline"
fi