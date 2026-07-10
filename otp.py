import random
def genotp():
    otp=''
    C_L=[chr(i) for i in range(ord('A'),ord('Z')+1)]
    s_l=[chr(i) for i in range(ord('a'),ord('z')+1)]
    for i in range(2):
        otp=otp+random.choice(C_L)+str(random.randint(0,9))+random.choice(s_l)
    return otp