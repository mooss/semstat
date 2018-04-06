import pickle

def save_object(obj, filename):
    pickle.dump(obj, open(filename, 'wb'))

def load_object(filename):
    return pickle.load(open(filename, 'rb'))
