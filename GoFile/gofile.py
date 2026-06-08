import requests
import argparse
import json
import xml.etree.ElementTree as ET

verbose = False
server = None

def getServer(verbose):
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

def uploadFile(filepath, verbose):
    if getServer(verbose) != 0:
        global server
        server = getServer(verbose)
        url = "https://" + getServer(verbose) + ".gofile.io/uploadFile"
        if verbose:
            print('Preparando para enviar el archivo: '+filepath)
        files = {'file': (filepath, open(filepath, 'rb'))}
        if verbose:
            print('Realizando petición a "'+url+'"')
        response = requests.post(url, files=files)
        if verbose:
            print('Petición Realizada')
        if response.status_code == 200:
            data = response.json()
            data["data"]["server"] = server
            return data

def downloadFile(server, fileId, fileName, verbose):
    url = f"https://{server}.gofile.io/download/{fileId}/{fileName}"
    if verbose:
        print('Realizando petición a "'+url+'"')
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data

def downloadFileURL(url, verbose):
    if verbose:
        print('Realizando petición a "'+url+'"')
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data

def process_data(uploadedFile, format="json", verbose=verbose):
    def recursive_conversion(value):
        if isinstance(value, dict):
            return {key: recursive_conversion(val) for key, val in value.items()}
        return value

    processed_data = recursive_conversion(uploadedFile)

    if format == "json":
        return json.dumps(processed_data, indent=4)
    elif format == "xml":
        def dict_to_xml(dictionary, root):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    elem = ET.Element(key)
                    dict_to_xml(value, elem)
                else:
                    elem = ET.Element(key)
                    elem.text = str(value)
                root.append(elem)
            return root

        root = ET.Element("uploadedFile")
        dict_to_xml(processed_data, root)
        xml_data = ET.tostring(root, encoding="unicode")
        xml_data = '<?xml version="1.0" encoding="UTF-8" ?>'+xml_data
        return xml_data
    elif format == "plaintext":
        def dict_to_plaintext(dictionary, indent=0):
            result = ""
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    result += " " * indent + f"{key} :\n{dict_to_plaintext(value, indent + 4)}"
                else:
                    result += " " * indent + f"{key.ljust(15)} : {value}\n"
            return result

        return dict_to_plaintext(processed_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Programa para cargar y descargar archivos en GoFile.io")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo Verbose: Mostrar todos los datos")
    parser.add_argument("-d", "--download-url", nargs=1, metavar=("url"), help="Descargar archivo por URL")
    parser.add_argument("-s", "--download", nargs=3, metavar=("server", "fileId", "fileName"), help="Descargar archivo por server, fileId y fileName")
    parser.add_argument("-u", "--upload", help="Cargar archivo desde la ruta local")
    parser.add_argument("--json", action="store_true", help="Devolver datos en formato JSON")
    parser.add_argument("--xml", action="store_true", help="Devolver datos en formato XML")
    parser.add_argument("--plaintext", action="store_true", help="Devolver datos en formato plano")
    parser.add_argument("-o", "--output", help="Guardar datos en un archivo")

    args = parser.parse_args()

    if args.verbose:
        print("Modo Verbose habilitado.")
        verbose = True

    if args.download_url:
        data = downloadFileURL(args.download_url[0])
    elif args.download:
        server, fileId, fileName = args.download
        data = downloadFile(server, fileId, fileName,verbose)
    elif args.upload:
        data = uploadFile(args.upload,verbose)
    else:
        filepath = input("Ruta del archivo a cargar (/home/user/file.txt): ")
        data = uploadFile(filepath,verbose)

    # Si no se especifica ninguno de los formatos, se utiliza plaintext como formato predeterminado
    if not (args.json or args.xml or args.plaintext):
        args.plaintext = True

    processed_data = process_data(data, format="json" if args.json else "xml" if args.xml else "plaintext",verbose=verbose)

    if args.output:
        with open(args.output, "w") as output_file:
            output_file.write(processed_data)
            if verbose:
                print(f'Datos guardados en {args.output}')
    else:
        print(processed_data)
