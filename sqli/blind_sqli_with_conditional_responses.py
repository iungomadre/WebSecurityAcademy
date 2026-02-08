import string

AVAILABLE_CHARACTERS = sorted(string.printable)


example = 'example password'

def get_current_character(password_index):
    '''
    Utility method adjusting the behavior to simulate DB query
    
    :param password_index: index of a char within password we're checking
    '''
    try:
        char = example[password_index - 1]
        return char
    except IndexError:
        return ''

def is_less(password_index, checked_character):
    return get_current_character(password_index) < checked_character

def is_hit(password_index, checked_character):
    return get_current_character(password_index) == checked_character


def find_char_for_index(password_index, start, stop):
    if start > stop:
        return None

    checked_index = (start + stop) // 2
    checked_character = AVAILABLE_CHARACTERS[checked_index]

    if is_less(password_index, checked_character):
        return find_char_for_index(password_index, start, checked_index - 1)
    else:
        if is_hit(password_index, checked_character):
            return checked_character
        else:
            return find_char_for_index(password_index, checked_index + 1, stop)



def detect_password():
    password = ''
    char_index = 1

    while True:
        char = find_char_for_index(char_index, 0, len(AVAILABLE_CHARACTERS) - 1)
        if not char:
            break
        else:
            password += char
            char_index += 1

    return password


      

password = detect_password()
print(password)

