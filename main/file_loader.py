import os

class FileLoader:
    fileHandle = None

    def loadFile(self, filePath):
        fileHandle = open(filePath, "r")
        self.fileHandle = fileHandle
        return fileHandle.read()

    def disposeFile(self):
        self.fileHandle.close()