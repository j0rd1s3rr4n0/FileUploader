import argparse
import os
import tempfile
from tkinter import Tk

from data_processing import DataProcessor
from encryption import Encryption
from http_requests import HTTPRequest


def copy_to_clipboard(text):
    root = Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()


def parse_args():
    parser = argparse.ArgumentParser(description="Programa para cargar y descargar archivos en GoFile.io")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo Verbose: Mostrar todos los datos")
    parser.add_argument("-d", "--download-url", nargs=1, metavar=("url"), help="Descargar archivo por URL")
    parser.add_argument(
        "-s",
        "--download",
        nargs=3,
        metavar=("server", "fileId", "fileName"),
        help="Descargar archivo por server, fileId y fileName",
    )
    parser.add_argument("-u", "--upload", help="Cargar archivo desde la ruta local")
    parser.add_argument("--json", action="store_true", help="Devolver datos en formato JSON")
    parser.add_argument("--xml", action="store_true", help="Devolver datos en formato XML")
    parser.add_argument("--plaintext", action="store_true", help="Devolver datos en formato plano")
    parser.add_argument("-o", "--output", help="Guardar datos en un archivo")
    parser.add_argument("--copy", action="store_true", help="Copiar la salida procesada al portapapeles")
    parser.add_argument("--encrypt", action="store_true", help="Cifrar el archivo antes de subirlo")
    parser.add_argument("--password", help="Contraseña para cifrar o descifrar archivos")
    parser.add_argument("--decrypt-file", help="Descifrar un archivo local previamente cifrado")
    parser.add_argument("--decrypt-output", help="Ruta de salida para --decrypt-file")
    return parser.parse_args()


def decrypt_local_file(args):
    try:
        decrypted_path = Encryption.decrypt_file(args.decrypt_file, args.password, args.decrypt_output)
    except (OSError, ValueError) as exc:
        print(f"Error al descifrar: {exc}")
        return 1

    print(f"Archivo descifrado: {decrypted_path}")
    return 0


def encrypt_for_upload(filepath, password, verbose):
    encrypted_name = os.path.basename(filepath) + ".enc"
    encrypted_temp_path = os.path.join(tempfile.gettempdir(), encrypted_name)
    encrypted_path = Encryption.encrypt_file(filepath, password, encrypted_temp_path)
    if verbose:
        print(f"Archivo cifrado temporal: {encrypted_path}")
    return encrypted_path


def main():
    args = parse_args()

    if args.verbose:
        print("Modo Verbose habilitado.")

    if args.decrypt_file:
        if not args.password:
            print("Error: --password es obligatorio cuando se usa --decrypt-file")
            return 1
        return decrypt_local_file(args)

    data = None
    upload_path = None
    encrypted_temp_path = None

    if args.download_url:
        data = HTTPRequest.download_file_url(args.download_url[0], args.verbose)
    elif args.download:
        server, fileId, fileName = args.download
        data = HTTPRequest.download_file(server, fileId, fileName, args.verbose)
    elif args.upload:
        upload_path = args.upload
    else:
        upload_path = input("Ruta del archivo a cargar (/home/user/file.txt): ")

    if upload_path:
        if args.encrypt:
            if not args.password:
                print("Error: --password es obligatorio cuando se usa --encrypt")
                return 1
            encrypted_temp_path = encrypt_for_upload(upload_path, args.password, args.verbose)
            upload_path = encrypted_temp_path

        try:
            data = HTTPRequest.upload_file(upload_path, args.verbose)
        finally:
            if encrypted_temp_path and os.path.exists(encrypted_temp_path):
                os.remove(encrypted_temp_path)

    if data is None:
        print("No se recibieron datos del servicio.")
        return 1

    if not (args.json or args.xml or args.plaintext):
        args.plaintext = True

    processed_data = DataProcessor.process_data(
        data,
        format="json" if args.json else "xml" if args.xml else "plaintext",
        verbose=args.verbose,
    )

    if args.output:
        with open(args.output, "w") as output_file:
            output_file.write(processed_data)
            if args.verbose:
                print(f"Datos guardados en {args.output}")
    else:
        print(processed_data)

    if args.copy:
        try:
            copy_to_clipboard(processed_data)
            print("Salida copiada al portapapeles.")
        except Exception as exc:
            print(f"No se pudo copiar al portapapeles: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
