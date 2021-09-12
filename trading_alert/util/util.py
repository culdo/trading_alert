import pickle as pk


def load_ta():
    ta = pk.load(file=open('ta.pkl', 'rb'))
    ta.restore()
