import string
import random

def generate_random_filename(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length)) + '.mp4'
