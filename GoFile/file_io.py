class FileIO:
    @staticmethod
    def read_file(filepath):
        with open(filepath, "r") as file:
            return file.read()

    @staticmethod
    def write_file(filepath, data):
        with open(filepath, "w") as file:
            file.write(data)

