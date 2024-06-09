import sys 

path = sys.path[0] + '/../config-files/mqtt.config'
print("CONFIG PATH: " + path)



def get_topics():
    file = open(path)
    topics = []
    for line in file.readlines():
        line = line.strip()
        line = line.split(" ")
        if line[0] == 'topic':
            topics.append(line[1])
    return topics

def get_address():
    file = open(path)
    for line in file.readlines():
        line = line.strip()
        line = line.split(" ")
        if line[0] == 'address':
                return line[1]
    return None

def get_password():
    file = open(path)
    for line in file.readlines():
        line = line.strip()
        line = line.split(" ")
        if line[0] == 'password':
                return line[1]
    return None


def get_login():
    file = open(path)
    for line in file.readlines():
        line = line.strip()
        line = line.split(" ")
        if line[0] == 'login':
                return line[1]
    return None

def get_config():
    return { 'address' : get_address(),
              'topics' : get_topics(),
              'login' : get_login(),
              'password' : get_password()}
