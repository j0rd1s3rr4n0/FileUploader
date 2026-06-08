import json
from pathlib import Path

import requests


class HTTPRequest:
    UPLOAD_URL = "https://upload.gofile.io/uploadfile"

    @staticmethod
    def get_server(verbose):
        url = "https://api.gofile.io/getServer"
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(json.dumps(response.json()))
            if data["status"] == "ok":
                servername = data["data"]["server"]
                if verbose:
                    print("La solicitud GET exitosa. JSON PARSEABLE")
                return servername
            if verbose:
                print("La solicitud GET exitosa. JSON NO PARSEABLE")
            return 0

        if verbose:
            print("La solicitud GET no fue exitosa.")
        return 0

    @staticmethod
    def upload_file(filepath, verbose):
        file_path = Path(filepath)
        if verbose:
            print("Preparando para enviar el archivo: " + str(file_path))
            print('Realizando peticion a "' + HTTPRequest.UPLOAD_URL + '"')

        with file_path.open("rb") as file_handle:
            files = {"file": (file_path.name, file_handle)}
            response = requests.post(HTTPRequest.UPLOAD_URL, files=files)

        if verbose:
            print("Peticion realizada")
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def download_file(server, fileId, fileName, verbose):
        url = f"https://{server}.gofile.io/download/{fileId}/{fileName}"
        if verbose:
            print('Realizando peticion a "' + url + '"')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def download_file_url(url, verbose):
        if verbose:
            print('Realizando peticion a "' + url + '"')
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
