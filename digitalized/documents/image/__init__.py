from typing import Union, Callable, Any
from io import BytesIO
import zipfile
from .image import (
    ImageObject, BuilderInterfaceImage, LibImage,
    image_bytes_to_opencv, image_opencv_to_bytes, ImageExtension
)
from digitalized.types.array import ArrayList, T
from soup_files import File, Directory, InputFiles


class ImageStream(ArrayList[ImageObject]):

    def __init__(self, items: list[ImageObject] = None, lib_image: LibImage = "opencv", **kwargs) -> None:
        super().__init__(items)
        self.__lib_img: LibImage = lib_image

    def apply(self, func: Callable[[ImageObject], Any]) -> ArrayList[Any]:
        return ArrayList([func(item) for item in self])

    def set_landscape(self):
        for num, img in enumerate(self):
            self[num].set_landscape()

    def get_current_library(self) -> LibImage:
        return self.__lib_img

    def set_current_library(self, lib_img: LibImage):
        self.__lib_img = lib_img

    def add_image(self, img: Union[bytes, ImageObject]):
        if isinstance(img, bytes):
            img = ImageObject.create_from_bytes(img, library=self.get_current_library())
        self.append(img)

    def add_images(self, images: list[Union[bytes, ImageObject]]):
        for im in images:
            self.add_image(im)

    def add_file_image(self, file: File):
        img = ImageObject.create_from_file(file, library=self.get_current_library())
        self.add_image(img)

    def add_files_image(self, imgs: list[File]):
        for f in imgs:
            self.add_file_image(f)

    def add_dir_image(self, dir_img: Directory):
        _imgs = InputFiles(dir_img).images
        self.add_files_image(_imgs)

    def to_zip(self, prefix: str = None) -> BytesIO:
        if prefix is None:
            prefix = 'imagem'
        # Salvar em zip
        buff_zip = BytesIO()
        with zipfile.ZipFile(buff_zip, "w") as zipf:
            for num, img in enumerate(self):
                zipf.writestr(
                    f'{prefix}-{num+1}.{img.get_output_extension()}',
                    img.to_bytes(),
                )
        # Salvar o zip em disco para download
        buff_zip.seek(0)
        return buff_zip

    def to_files(self, output_dir: Directory, *, prefix: str = None):
        pass
