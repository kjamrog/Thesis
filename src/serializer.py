import pickle

def load_object(path):
    f = open(path, 'rb')
    data = pickle.load(f)
    f.close()
    return data

def save_object(path, data):
    output = open(path, 'wb')
    pickle.dump(data, output)
    output.close()