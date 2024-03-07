import argparse
from http_requests import HTTPRequest
from data_processing import DataProcessor
from file_io import FileIO
from encryption import Encryption

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
    print(args)

    if args.verbose:
        print("Modo Verbose habilitado.")

    if hasattr(args, 'download_url') and args.download_url:
        data = HTTPRequest.download_file_url(args.download_url[0], args.verbose)
    elif args.download:
        server, fileId, fileName = args.download
        data = HTTPRequest.download_file(server, fileId, fileName, args.verbose)
    elif args.upload:
        data = HTTPRequest.upload_file(args.upload, args.verbose)
    else:
        filepath = input("Ruta del archivo a cargar (/home/user/file.txt): ")
        data = HTTPRequest.upload_file(filepath, args.verbose)

    # Si no se especifica ninguno de los formatos, se utiliza plaintext como formato predeterminado
    if not (args.json or args.xml or args.plaintext):
        args.plaintext = True

    processed_data = DataProcessor.process_data(data, format="json" if args.json else "xml" if args.xml else "plaintext", verbose=args.verbose)

    if args.output:
        with open(args.output, "w") as output_file:
            output_file.write(processed_data)
            if args.verbose:
                print(f'Datos guardados en {args.output}')
    else:
        print(processed_data)
