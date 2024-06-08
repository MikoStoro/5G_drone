import sys 

path = sys.path[0] + '/../config-files/heart.config'
print("CONFIG PATH: " + path)



def get_sensor_topics():
    file = open(path)
    topics = []
    for line in file.readlines():
        line = line.strip()
        line = line.split(" ")
        if line[0] == 'sensor_topic':
            topics.append(line[1])
    return topics

def set_settings():
    file = open(path)
    settings = {}
    for line in file.readlines():
        line = line.strip()
        line = line.split(" ")
        if line[0] == 'settings':
            settings[line[1]] = int(line[2])
    return settings



def get_config():
    return { 'settings' : set_settings(),
			'sensor_topics' : get_sensor_topics()}
