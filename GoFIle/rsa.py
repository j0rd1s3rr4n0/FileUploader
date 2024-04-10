from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import datetime
import os,sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Función para generar claves RSA
def generate_rsa_keys(filename):
    print(filename)
    splitter_filepath = filename.split("/")
    if(len(splitter_filepath) == 1):
        splitter_filepath = filename.split("\\")
    filename = splitter_filepath[len(splitter_filepath)-1]
    print(filename)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    x = datetime.datetime.now()
    date_str = x.strftime("%d_%m_%Y_%H_%M_%S")
    os.makedirs(f"keys/{filename}_{date_str}", exist_ok=True)
    
    # Guardar la clave privada en un archivo
    with open(f"keys/{filename}_{date_str}/private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        print("Saved Private Key:", os.path.abspath(f"keys/{filename}_{date_str}/private_key.pem"))

    # Obtener la clave pública
    public_key = private_key.public_key()

    # Guardar la clave pública en un archivo
    # with open(f"keys/{filename}_{date_str}/public_key.pem", "wb") as f:
    #     f.write(public_key.public_bytes(
    #         encoding=serialization.Encoding.PEM,
    #         format=serialization.PublicFormat.SubjectPublicKeyInfo
    #     ))
    #     print("Saved Public Key:", os.path.abspath(f"keys/{filename}_{date_str}/public_key.pem"))

    return private_key, public_key

# Función para encriptar el contenido de un archivo usando RSA
def encrypt_file(filename, public_key,metacrypt=".enc"):
    with open(filename, "rb") as f:
        plaintext = f.read()

    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    encrypted_filename = filename + metacrypt

    with open(encrypted_filename, "wb") as f:
        f.write(ciphertext)

    return encrypted_filename

# Función para cargar la clave privada desde un archivo
def load_private_key(filename):
    with open(filename, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

# Función para desencriptar el contenido de un archivo usando RSA
def decrypt_file(encrypted_filename, private_key):
    with open(encrypted_filename, "rb") as f:
        ciphertext = f.read()

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return plaintext

def selectFile(type,message):
    if type == "dec":
        return askopenfilename(title=message, filetypes=[
            ("Text Files", "*.txt"),
            ("Portable Document Format File", "*.pdf"),
            ("Microsoft Word Files", "*.docx *.doc"),
            ("Microsoft Excel Files", "*.xlsx *.xls"),
            ("Microsoft PowerPoint Files", "*.pptx *.ppt"),
            ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif *.svg"),
            ("Audio Files", "*.mp3 *.wav *.ogg *.flac *.wma *.aac *.aiff *.alac *.m4a"),
            ("Video Files", "*.mp4 *.avi *.mov *.flv *.wmv *.mkv *.webm *.vob *.m4v *.3gp"),
            ("Compressed Files", "*.zip *.rar *.7z *.tar *.gz *.bz2 *.xz *.zst *.lzma *.lz4 *.lzip *.lzo *.cab *.arj *.arc *.pkg *.deb *.rpm *.apk *.dmg *.iso *.img"),
            ("Executable Files", "*.exe *.msi *.apk *.app *.bat *.bin *.cgi *.com *.gadget *.jar *.pif *.wsf"),
            ("Script Files", "*.sh *.bash *.ps1 *.py *.pl *.rb *.js *.vbs *.ahk *.cmd *.c *.cpp *.h *.hpp *.java *.cs *.php *.html *.css *.xml *.json *.yaml *.yml *.toml *.ini *.cfg *.conf *.cnf *.env *.envrc *.env.example *.env.local *.env.test *.env.development *.env.production *.env.staging *.env.ci *.env.local"),
            ("All Files", "*.*"),
        ])
    else:
        return askopenfilename(title=message, filetypes=[
            ("RSA Keys", "*.pem"),
            ("Encripted Files", "*.enc"),
            ("Dash files", "*.___"),
            ("Encripted JkFiles", "*.jk"),
            ("Parthenoun files", "*.pth"),
        ])
        
	

def menu():
    print("1. Encriptar archivo")
    print("2. Desencriptar archivo")
    print("3. Salir")
    opcion = input("Ingrese una opción: ")
    return opcion

"""
def main():
    res = menu()
    if( res== "1"): 
        filename = selectFile("dec",message="Select File To DeCrypt")
        if os.path.isfile(filename):
            print("filename:", filename)
            private_key, public_key = generate_rsa_keys(filename)
            encrypted_filename = encrypt_file(filename, public_key)
            print("Created", encrypted_filename,end="\n\n\n")
        else:
            print("El archivo no existe. Intente de nuevo.")
            pass
    elif(res == "2"):
        filename = selectFile("dec",message="Select File To DeCrypt")
        if os.path.isfile(filename):
            print("filename:", filename)
            private_key = load_private_key(selectFile("key",message="Select Private Key"))
            plaintext = decrypt_file(filename, private_key)
            decrypted_filename = filename[:-4]  
            with open(decrypted_filename, "wb") as f:
                f.write(plaintext)
            print("Decrypted content saved in:", decrypted_filename)
        else:
            print("El archivo no existe. Intente de nuevo.")
            pass    
    elif(res == "3"):
        exit()
            
Tk().withdraw()
main()
"""    
    

