from __future__ import annotations
from abc import ABC, abstractmethod
from io import BytesIO
import zipfile
from soup_files import Directory, File


class OutputStream(ABC):

    @abstractmethod
    def save_zip_file(self, list_bytes: list[bytes], *, file_path: File, prefix: str) -> None:
        pass

    @abstractmethod
    def save_zip(self, list_bytes: list[bytes], *, prefix: str) -> BytesIO:
        pass


class ZipOutputStream(OutputStream):

    def __init__(self, output_extension: str):
        self.output_extension = output_extension
        self.count: int = 0

    def save_zip_file(self, list_bytes: list[bytes], *, file_path: File, prefix: str) -> None:
        final_bytes = self.save_zip(list_bytes, prefix=prefix)
        final_bytes.seek(0)
        with open(file_path.absolute(), "wb") as f:
            f.write(final_bytes.getvalue())

    def save_zip(self, list_bytes: list[bytes], *, prefix: str) -> BytesIO:
        # Salvar em zip
        buff_zip = BytesIO()
        file_bytes: bytes
        with zipfile.ZipFile(buff_zip, "w") as zipf:
            for file_bytes in list_bytes:
                self.count += 1
                zipf.writestr(
                    f'{prefix}-{self.count}.{self.output_extension}',
                    file_bytes,
                )
        # Salvar o zip em disco para download
        buff_zip.seek(0)
        return buff_zip


__all__ = ['OutputStream', 'ZipOutputStream']
