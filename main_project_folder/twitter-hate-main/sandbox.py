
from deploy import Hate
while True:
    inp=input(f" Enter tweet to test ")
    k= Hate()
    k.cleanTrain()
    m=k.interface(inp)
    w= m['weight']
    label=max(w)
    
    label="NOT HATESPEECH" if label < 1 else "HATESPEECH"
    print(f'The test tweet is {label}')