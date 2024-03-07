import requests
import json

class HTTPRequest:
    @staticmethod
    def get_server(verbose):
        url = "https://api.gofile.io/getServer"
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(json.dumps(response.json()))
            if data['status'] == "ok":
                servername = data["data"]["server"]
                if verbose:
                    print("La solicitud GET exitosa. JSON PARSEABLE")
                return servername
            if verbose:
                print("La solicitud GET exitosa. JSON NO PARSEABLE")
            return 0
        else:
            if verbose:
                print("La solicitud GET no fue exitosa.")
            return 0

    @staticmethod
    def upload_file(filepath, verbose):
        def get_server(verbose):
            url = "https://api.gofile.io/getServer"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data['status'] == "ok":
                    servername = data["data"]["server"]
                    if verbose:
                        print("La solicitud GET exitosa. JSON PARSEABLE")
                    return servername
                if verbose:
                    print("La solicitud GET exitosa. JSON NO PARSEABLE")
                return 0
            else:
                if verbose:
                    print("La solicitud GET no fue exitosa.")
                return 0

        if get_server(verbose) != 0:
            server = get_server(verbose)
            url = f"https://{server}.gofile.io/uploadFile"
            if verbose:
                print('Preparando para enviar el archivo: '+filepath)
            files = {'file': (filepath, open(filepath, 'rb'))}
            if verbose:
                print('Realizando petición a "'+url+'"')
            response = requests.post(url, files=files)
            if verbose:
                print('Petición Realizada')
            if response.status_code == 200:
                return response.json()

    @staticmethod
    def download_file(server, fileId, fileName, verbose):
        url = f"https://{server}.gofile.io/download/{fileId}/{fileName}"
        if verbose:
            print('Realizando petición a "'+url+'"')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()

    @staticmethod
    def download_file_url(url, verbose):
        if verbose:
            print('Realizando petición a "'+url+'"')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()