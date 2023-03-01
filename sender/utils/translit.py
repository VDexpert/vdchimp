from transliterate import translit

def do(string):
    string = '-'.join(translit(string, 'ru', reversed=True).lower().split(' '))
    return ''.join(x for x in string if x.isalnum() or x == '-')