import requests
impprt argvs
import json

def getServer():
    url = "https://api.gofile.io/getServer"
    response = requests.get(url)

    if response.status_code == 200:
        data = json.loads(json.dumps(response.json()))
        if data['status'] == "ok":
            servername = data["data"]["server"]
            return servername
        return 0
    else:
        print("La solicitud GET no fue exitosa.")
        return 0

def uploadFile(filepath=None):
    if(filepath==None):
        filepath = input("File Path (/home/user/file.txt) > ")
    if(getServer()!=0):
        url = "https://"+getServer()+".gofile.io/uploadFile"
        files = {'file': (filepath, open(filepath, 'rb'))}
        response = requests.post(url, files=files)
        if response.status_code == 200:
            data = response.json()
            print(data)
        else:
            print("La solicitud POST no fue exitosa.")


# Modo Verbose Mostrar todos los datos
# -v --json o --xml o --plaintext

# Download File
# --download URL
# --download https://store6.gofile.io/download/afc48555-cf6f-4c2a-b5a9-27c4c286553b/text.txt

uploadFile()
