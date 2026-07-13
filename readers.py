from abc import ABC, abstractmethod
import json

class FileReader(ABC):
    #interface for different file formats
    @abstractmethod
    def read(self, file_path: str) -> list:
        pass

class JSONReader(FileReader):
    def read(self, file_path: str) -> list:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)