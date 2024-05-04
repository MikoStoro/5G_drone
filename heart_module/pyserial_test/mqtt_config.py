path = 'mqtt.config'



def get_topics():
    file = open(path)
    topics = []
    started = False
    for line in file.readlines():
        line = line.strip()
        if started:
            if line[0] == '[':
                started = False
                break
            topics.append(line)
        else:
            if line == '[topics]':
                started = True
    return topics

def get_address():
     file = open(path)