path = 'config-files/mqtt.config'



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
            if line[0] == 'passsword':
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
              'topics' : get_topic(),
              'login' : get_login(),
              'password' : get_password()}
