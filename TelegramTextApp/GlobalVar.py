api = 'API'
folder = 'data'
admin = 0

def TTA(API, ADMIN, FOLDER):
    global api, admin, folder
    api = API
    folder = FOLDER
    admin = ADMIN

    from .code import *