import os
import sys

from anonfilesnew import main


if __name__ == "__main__":
    os.system("title AnonFilesNew Uploader by J0rd1s3rr4n0")
    exit_code = main()
    print("\nWindow will close in 5 minutes.")
    os.system("timeout /t 300 > %TEMP%/null")
    sys.exit(exit_code)
