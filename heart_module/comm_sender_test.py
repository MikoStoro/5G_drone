
time
pipe = open("./comm_pipe", "a")
pipe.write("./net_state.sh 8.8.8.8")
output = open("./pipe_output", "r")
print(output.read())
pipe.close()
output.close()