#!/usr/bin/env python3
#
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Literal, Any
from io import BytesIO
from PIL import Image, ImageOps, ImageFilter
from cv2.typing import MatLike
import cv2
import numpy as np
from soup_files import File
from digitalized.documents.erros import InvalidSourceImageError, NotImplementedInvertColor
from digitalized.types.core import ObjectAdapter

LibImage = Literal["opencv", "pil"]
BackgroundColor = Literal["gray", "black"]
ImageExtension = Literal["jpg", "jpeg", "png"]
RotationAngle = Literal[90, 180, 270]


def image_bytes_to_opencv(img_bytes: bytes) -> cv2.typing.MatLike:
    """Converte os bytes de uma imagem em objeto opencv MatLike"""
    nparr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)


def image_opencv_to_bytes(img: cv2.typing.MatLike, image_extension: ImageExtension = "png") -> bytes:
    """Convert um objeto opencv MatLike em bytes de imagem"""
    _, buffer = cv2.imencode(f'.{image_extension}', img)  # Codifica como PNG (ou use '.jpg' para JPEG)
    return buffer.tobytes()  # Obtém os bytes da imagem


class ABCInvertColor(ABC):

    @abstractmethod
    def get_lib_image(self) -> LibImage:
        pass

    @abstractmethod
    def is_gaussian_blur(self) -> bool:
        pass

    @abstractmethod
    def set_image_bytes(self, img_bytes: bytes):
        pass

    @abstractmethod
    def get_image_bytes(self) -> bytes:
        pass

    @abstractmethod
    def set_background(self, background: BackgroundColor = "gray"):
        pass

    @abstractmethod
    def set_gaussian_blur(self):
        pass

    def to_file(self, output_path: File):
        if self.get_lib_image() == "opencv":
            cv2.imwrite(
                output_path.absolute(), image_bytes_to_opencv(self.get_image_bytes())
            )
        elif self.get_lib_image() == "pil":
            img: Image.Image = Image.open(self.get_image_bytes())
            img.save(output_path.absolute(), 'png')

    def to_bytes(self) -> bytes:
        return self.get_image_bytes()

    def to_pil(self) -> Image.Image:
        """Converte a propriedade bytes em imagem PIL"""
        return Image.open(BytesIO(self.get_image_bytes()))

    def to_opencv(self) -> cv2.typing.MatLike:
        """Converte a propriedade bytes em imagem objeto opencv"""
        return image_bytes_to_opencv(self.get_image_bytes())


class ABCImageObject(ABC):
    """
    Classe abstrata base para objetos de imagem.
    """

    def __init__(self, image_extension: ImageExtension = "png"):
        self.__output_extension: ImageExtension = image_extension
        self.__invert_color: ImageInvertColor = None

    @abstractmethod
    def get_width(self) -> int:
        """Retorna a largura da imagem."""
        pass

    @abstractmethod
    def get_height(self) -> int:
        """Retorna a altura da imagem."""
        pass

    @abstractmethod
    def set_image_bytes(self, img_bytes: bytes):
        pass

    @abstractmethod
    def get_image_bytes(self) -> bytes:
        pass

    @abstractmethod
    def get_current_library(self) -> LibImage:
        pass

    @abstractmethod
    def set_optimize(self):
        pass

    @abstractmethod
    def set_paisagem(self):
        pass

    @abstractmethod
    def set_rotation(self, rotation: RotationAngle = 90):
        pass

    @abstractmethod
    def set_background(self, color: BackgroundColor = "gray"):
        pass

    @abstractmethod
    def set_gaussian(self):
        pass

    def get_invert_color(self) -> ImageInvertColor:
        if self.__invert_color is None:
            self.__invert_color = ImageInvertColor.create_from_bytes(
                self.get_image_bytes(), library=self.get_current_library()
            )
        return self.__invert_color

    def set_invert_color(self, invert: ImageInvertColor):
        self.__invert_color = invert

    @abstractmethod
    def is_paisagem(self) -> bool:
        """
        Retorna True se a imagem estiver em modo paisagem.
        """
        pass

    def is_gaussian(self) -> bool:
        return self.get_invert_color().is_gaussian_blur()

    def get_output_extension(self) -> ImageExtension:
        return self.__output_extension

    def set_output_extension(self, fmt: ImageExtension):
        self.__output_extension = fmt

    def to_image_pil(self) -> Image.Image:
        return Image.open(BytesIO(self.get_image_bytes()))

    def to_image_opencv(self) -> cv2.typing.MatLike:
        # nparr = np.frombuffer(self.get_image_bytes(), np.uint8)
        # return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image_bytes_to_opencv(self.get_image_bytes())

    def to_bytes(self) -> bytes:
        return self.get_image_bytes()

    def to_file(self, filepath: File):
        if self.get_current_library() == "pil":
            try:
                self.to_image_pil().save(filepath.absolute(), format=self.get_output_extension())
            except Exception as e:
                raise Exception(f"{__class__.__name__} Erro ao salvar imagem PIL: {e}")
        elif self.get_current_library() == "opencv":
            try:
                cv2.imwrite(filepath.absolute(), self.to_image_opencv())
            except Exception as e:
                raise Exception(f"Erro ao salvar imagem OpenCV: {e}")


# =============================================================================#
# Inverter cores em imagens
# =============================================================================#
class ImplementInvertColorOpenCv(ABCInvertColor):
    """
        Escurecer texto em imagens.
    """

    def __init__(self, image_bytes: bytes):
        super().__init__()
        if not isinstance(image_bytes, bytes):
            raise InvalidSourceImageError(
                f'{__class__.__name__} Use: bytes, não {type(image_bytes)}'
            )
        self.__image_bytes: bytes = image_bytes
        self.__gaussian_blur: bool = False

    def get_lib_image(self) -> LibImage:
        return "opencv"

    def set_image_bytes(self, img_bytes: bytes):
        self.__image_bytes = img_bytes

    def get_image_bytes(self) -> bytes:
        return self.__image_bytes

    def is_gaussian_blur(self) -> bool:
        return self.__gaussian_blur

    def set_gaussian_blur(self):
        if self.is_gaussian_blur():
            return
        # Aplica um filtro Gaussiano para reduzir o ruído
        #_blurred: MatLike = cv2.GaussianBlur(image_bytes_to_opencv(self.__image_bytes), (5, 5), 0)
        _blurred = cv2.bilateralFilter(image_bytes_to_opencv(self.__image_bytes), d=9, sigmaColor=75, sigmaSpace=75)
        self.__image_bytes = image_opencv_to_bytes(_blurred)
        self.__gaussian_blur = True

    def set_background(self, background: BackgroundColor = "gray"):
        if background == "gray":
            self.__set_background_gray()
        elif background == "black":
            self.__set_background_black()
        else:
            raise ValueError(f'{__class__.__name__} Use {BackgroundColor}, não {background}')

    def __set_background_black(self):
        self.set_gaussian_blur()
        # Aplica binarização adaptativa (texto branco, fundo preto)
        binary: MatLike = cv2.adaptiveThreshold(
            image_bytes_to_opencv(self.__image_bytes),
            150,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        self.__image_bytes = image_opencv_to_bytes(binary)
        _result: MatLike = cv2.bitwise_not(image_bytes_to_opencv(self.__image_bytes))
        self.__image_bytes = image_opencv_to_bytes(_result)

    def __set_background_gray(self):
        self.set_gaussian_blur()
        # Aplica binarização adaptativa (texto preto, fundo branco)
        _img: cv2.typing.MatLike = image_bytes_to_opencv(self.__image_bytes)
        _binary = cv2.adaptiveThreshold(
            _img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,  # Inverte o texto para ser branco inicialmente
            11,
            2
        )
        self.__image_bytes = image_opencv_to_bytes(_binary)
        #_result: MatLike = cv2.bitwise_not(image_bytes_to_opencv(self.__image_bytes))
        #self.__image_bytes = image_opencv_to_bytes(_result)


class ImplementInvertColorPIL(ABCInvertColor):
    """
        Implementação da inversão de cores usando PIL (Pillow).
    """

    def __init__(self, image_bytes: bytes):
        super().__init__()
        if not isinstance(image_bytes, bytes):
            raise InvalidSourceImageError(
                f'{__class__.__name__} Use: bytes, não {type(image_bytes)}'
            )
        self.__img_bytes: bytes = image_bytes
        self.__gaussian_blur: bool = False

    def get_lib_image(self) -> LibImage:
        return "pil"

    def is_gaussian_blur(self) -> bool:
        return self.__gaussian_blur

    def set_image_bytes(self, img_bytes: bytes):
        self.__img_bytes = img_bytes

    def get_image_bytes(self) -> bytes:
        return self.__img_bytes

    def set_gaussian_blur(self):
        if self.is_gaussian_blur():
            return
        img_pil = Image.open(BytesIO(self.__img_bytes))
        # Aplicar um desfoque semelhante ao cv2.GaussianBlur
        blurred: Image.Image = img_pil.filter(ImageFilter.GaussianBlur(radius=1))
        buff = BytesIO()
        blurred.save(buff, 'png')
        self.__img_bytes = buff.getvalue()
        buff.close()
        self.__gaussian_blur = True

    def set_background(self, background: BackgroundColor = "gray"):
        if background == "gray":
            self.__set_background_gray()
        elif background == "black":
            self.__set_background_black()

    def __set_background_black(self):
        img_pil = Image.open(BytesIO(self.__img_bytes))
        _result = ImageOps.invert(img_pil.convert("L"))  # Converte para escala de cinza
        buff = BytesIO()
        _result.save(buff, 'png')
        self.__img_bytes = buff.getvalue()
        buff.close()

    def __set_background_gray(self):
        # Abrir a imagem a partir dos bytes
        img_pil = Image.open(BytesIO(self.__img_bytes))

        # Converter para escala de cinza
        gray_img = img_pil.convert("L")

        # Inverter as cores
        inverted_img = ImageOps.invert(gray_img)

        # Aplicar um threshold invertido: força fundo branco e texto preto
        threshold = 128  # Ajuste conforme necessário
        binary_img = inverted_img.point(lambda x: 0 if x > threshold else 150)  # Invertido aqui!

        # Salvar de volta para bytes
        buff = BytesIO()
        binary_img.save(buff, 'PNG')
        self.__img_bytes = buff.getvalue()
        buff.close()


class ImageInvertColor(ObjectAdapter):
    """
        Escurecer texto em imagens.
    """

    def __init__(self, invert_color: ABCInvertColor):
        super().__init__()
        self._invert_color: ABCInvertColor = invert_color

    def get_implementation(self) -> ABCInvertColor:
        return self._invert_color

    def hash(self) -> int:
        return hash(self.get_image_bytes())

    def get_lib_image(self) -> LibImage:
        return self._invert_color.get_lib_image()

    def is_gaussian_blur(self) -> bool:
        return self._invert_color.is_gaussian_blur()

    def set_image_bytes(self, img_bytes: bytes):
        self._invert_color.set_image_bytes(img_bytes)

    def get_image_bytes(self) -> bytes:
        return self._invert_color.get_image_bytes()

    def set_gaussian_blur(self):
        self._invert_color.set_gaussian_blur()

    def set_background(self, background: BackgroundColor = "gray"):
        self._invert_color.set_background(background)

    def to_file(self, output_path: File):
        return self._invert_color.to_file(output_path)

    def to_bytes(self):
        return self._invert_color.to_bytes()

    @classmethod
    def create_from_file(cls, f: File, *, library: LibImage = "opencv") -> ImageInvertColor:
        bt = None
        with open(f.absolute(), 'rb') as file:
            bt = file.read()

        if library == "opencv":
            inv: ABCInvertColor = ImplementInvertColorOpenCv(bt)
        elif library == "pil":
            inv: ABCInvertColor = ImplementInvertColorPIL(bt)
        else:
            raise NotImplementedInvertColor(
                f'{__class__.__name__} Use: {LibImage}, não {type(library)}'
            )
        return cls(inv)

    @classmethod
    def create_from_bytes(cls, bt: bytes, *, library: LibImage = "opencv") -> 'ImageInvertColor':
        if library == "opencv":
            invert_color: ABCInvertColor = ImplementInvertColorOpenCv(bt)
        elif library == "pil":
            invert_color: ABCInvertColor = ImplementInvertColorPIL(bt)
        else:
            raise NotImplementedInvertColor(
                f'{__class__.__name__} Use: {LibImage}, não {type(library)}'
            )
        return cls(invert_color)


# =============================================================================#
# Manipulação de imagens
# =============================================================================#
class ImageObjectPIL(ABCImageObject):
    """
        Implementação de ImageObject usando PIL.
    """

    def __init__(self, image_bytes: bytes):
        super().__init__()
        if not isinstance(image_bytes, bytes):
            raise InvalidSourceImageError(
                f'{__class__.__name__} Use: bytes, não {type(image_bytes)}'
            )

        self.__img_bytes = image_bytes
        self.max_size: Tuple[int, int] = (1980, 720)  # Dimensões máximas, altere se necessário.
        try:
            img = Image.open(BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"{__class__.__name__}\nPIL: {e}")

        # Redimensionar, se as dimensões forem maior que self.max_size.
        if img.width > self.max_size[0] or img.height > self.max_size[1]:
            buff_image: BytesIO = BytesIO()
            img.save(buff_image, format='PNG', optimize=True, quality=80)
            self.__img_bytes = buff_image.getvalue()
            buff_image.seek(0)
            buff_image.close()
        del img

    def get_width(self) -> int:
        return self.to_image_pil().width

    def get_height(self) -> int:
        return self.to_image_pil().height

    def set_image_bytes(self, img_bytes: bytes):
        self.__img_bytes = img_bytes

    def get_image_bytes(self) -> bytes:
        return self.__img_bytes

    def get_current_library(self) -> LibImage:
        return "pil"

    def set_background(self, color: BackgroundColor = "gray"):
        if color == "gray":
            self.__set_background_gray()
        elif color == "black":
            self.__set_background_black()

    def __set_background_black(self):
        #inv = ImageInvertColor.create_from_bytes(self.to_bytes(), library="pil")
        inv = self.get_invert_color()
        inv.set_image_bytes(self.get_image_bytes())
        inv.set_background("black")
        self.__img_bytes = inv.to_bytes()

    def __set_background_gray(self):
        # inv = ImageInvertColor.create_from_bytes(self.to_bytes(), library="pil")
        inv = self.get_invert_color()
        inv.set_image_bytes(self.get_image_bytes())
        inv.set_background("gray")
        self.__img_bytes = inv.to_bytes()

    def is_paisagem(self) -> bool:
        """
        Retorna True se a imagem estiver em modo paisagem.
        """
        width, height = self.get_width(), self.get_height()
        return width > height

    def set_rotation(self, rotation: RotationAngle = 90):
        img = Image.open(BytesIO(self.__img_bytes))
        if rotation == 90:
            img = img.transpose(Image.Transpose.ROTATE_90)
        elif rotation == 180:
            img = img.transpose(Image.Transpose.ROTATE_180)
        elif rotation == 270:
            img = img.transpose(Image.Transpose.ROTATE_270)
        else:
            return
        new_bytes = BytesIO()
        img.save(new_bytes, format='png')
        self.__img_bytes = new_bytes.getvalue()
        new_bytes.close()

    def set_paisagem(self):
        if not self.is_paisagem():
            img = Image.open(BytesIO(self.__img_bytes))
            img = img.transpose(Image.Transpose.ROTATE_90)  # Rotaciona -90 graus
            new_bytes = BytesIO()
            img.save(new_bytes, format='png')
            self.__img_bytes = new_bytes.getvalue()
            new_bytes.close()

    def set_optimize(self):
        optimized_bytes = BytesIO()
        img = self.to_image_pil()
        img.save(optimized_bytes, format='PNG', optimize=True, quality=80)
        self.__img_bytes = optimized_bytes.getvalue()
        optimized_bytes.close()

    def set_gaussian(self):
        inv = ImageInvertColor.create_from_bytes(self.to_bytes(), library="pil")
        inv.set_gaussian_blur()
        self.__img_bytes = inv.to_bytes()


class ImageObjectOpenCV(ABCImageObject):
    """
        Implementação de ImageObject usando OpenCV.
    """

    def __init__(self, image_bytes):
        super().__init__()
        if not isinstance(image_bytes, bytes):
            raise ValueError(f'{__class__.__name__} Use: bytes, não {type(image_bytes)}')
        self.__image_bytes = image_bytes
        self.max_size: Tuple[int, int] = (1980, 720)

        try:
            nparr = np.frombuffer(self.__image_bytes, np.uint8)
            image_opencv: MatLike = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            print('-' * 80)
            raise ValueError(f"{__class__.__name__}: Bytes de imagem OpenCV inválidos")
        else:
            _dimensions = (image_opencv.shape[1], image_opencv.shape[0])  # (largura, altura)

        # Redimensionar se necessário
        if _dimensions[0] > self.max_size[0] or _dimensions[1] > self.max_size[1]:
            h, w = image_opencv.shape[:2]
            scale = min(self.max_size[0] / w, self.max_size[1] / h)
            new_size = (int(w * scale), int(h * scale))
            image_opencv = cv2.resize(image_opencv, new_size, interpolation=cv2.INTER_LANCZOS4)
            # Converter a imagem de volta para bytes
        _, encoded_img = cv2.imencode('.png', image_opencv)
        self.__image_bytes = encoded_img.tobytes()

    def get_width(self) -> int:
        return self.to_image_opencv().shape[1]

    def get_height(self) -> int:
        return self.to_image_opencv().shape[0]

    def set_image_bytes(self, img_bytes: bytes):
        self.__image_bytes = img_bytes

    def get_image_bytes(self) -> bytes:
        return self.__image_bytes

    def get_current_library(self) -> LibImage:
        return 'opencv'

    def set_background(self, color: BackgroundColor = "gray"):
        if color == "gray":
            self.__set_background_gray()
        elif color == "black":
            self.__set_background_black()

    def is_paisagem(self) -> bool:
        """
        Retorna True se a imagem estiver em modo paisagem.
        """
        width, height = self.get_width(), self.get_height()
        return width > height

    def set_rotation(self, rotation: RotationAngle = 90):
        nparr = np.frombuffer(self.__image_bytes, np.uint8)
        img: MatLike = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if rotation == 90:
            img: MatLike = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif rotation == 180:
            img: MatLike = cv2.rotate(img, cv2.ROTATE_180)
        elif rotation == 270:
            img: MatLike = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            img: MatLike = cv2.rotate(img, cv2.ROTATE_180)
        else:
            return
        success, encoded_image = cv2.imencode('.png', img)
        if success:
            self.__image_bytes = encoded_image.tobytes()

    def set_paisagem(self):
        if not self.is_paisagem():
            nparr = np.frombuffer(self.__image_bytes, np.uint8)
            img: MatLike = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img: MatLike = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)  # Rotaciona -90 graus
            success, encoded_image = cv2.imencode('.png', img)
            if success:
                self.__image_bytes = encoded_image.tobytes()

    def set_optimize(self):
        """
            Reduz o tamanho da imagem, e salva a imagen reduzida na propriedade bytes.
        """
        imagem: MatLike = self.to_image_opencv()
        _status, buffer = cv2.imencode(".png", imagem, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if _status:
            self.__image_bytes = buffer.tobytes()

    def __set_background_black(self):
        inv = ImageInvertColor.create_from_bytes(self.to_bytes(), library="opencv")
        inv.set_background('black')
        self.__image_bytes = inv.to_bytes()

    def __set_background_gray(self):
        inv = ImageInvertColor.create_from_bytes(self.to_bytes(), library="opencv")
        inv.set_background("gray")
        self.__image_bytes = inv.to_bytes()

    def set_gaussian(self):
        inv = ImageInvertColor.create_from_bytes(self.to_bytes(), library=self.get_current_library())
        inv.set_gaussian_blur()
        self.__image_bytes = inv.to_bytes()


class ImageObject(ObjectAdapter):
    """
        Facade para manipular imagens com PIL ou OPENCV
    """

    def __init__(self, img_obj: ABCImageObject):
        super().__init__()
        self.__implement_img: ABCImageObject = img_obj

    def get_implementation(self) -> ABCImageObject:
        return self.__implement_img

    def hash(self) -> int:
        return hash(self.__implement_img.get_image_bytes())

    def get_width(self) -> int:
        return self.__implement_img.get_width()

    def get_height(self) -> int:
        return self.__implement_img.get_height()

    def set_image_bytes(self, img_bytes: bytes):
        self.__implement_img.set_image_bytes(img_bytes)

    def get_image_bytes(self) -> bytes:
        return self.__implement_img.get_image_bytes()

    def get_current_library(self) -> LibImage:
        return self.__implement_img.get_current_library()

    def set_background(self, color: BackgroundColor = "gray"):
        self.__implement_img.set_background(color)

    def set_optimize(self):
        """
            Reduz o tamanho da imagem, e salva a imagen reduzida na propriedade bytes.
        """
        self.__implement_img.set_optimize()

    def set_rotation(self, rotation: RotationAngle = 90):
        self.__implement_img.set_rotation(rotation)

    def set_paisagem(self):
        self.__implement_img.set_paisagem()

    def set_gaussian(self):
        self.__implement_img.set_gaussian()

    def to_image_pil(self) -> Image.Image:
        return self.__implement_img.to_image_pil()

    def to_image_opencv(self) -> cv2.typing.MatLike:
        return self.__implement_img.to_image_opencv()

    def to_file(self, f: File):
        self.__implement_img.to_file(f)

    def is_paisagem(self) -> bool:
        return self.__implement_img.is_paisagem()

    def to_bytes(self) -> bytes:
        return self.__implement_img.to_bytes()

    @classmethod
    def create_from_bytes(cls, image_bytes: bytes, *, library: LibImage = "opencv") -> 'ImageObject':
        if library == "pil":
            img = ImageObjectPIL(image_bytes)
        elif library == "opencv":
            img = ImageObjectOpenCV(image_bytes)
        else:
            raise ValueError("Biblioteca de imagem inválida.")
        return cls(img)

    @classmethod
    def create_from_file(cls, filepath: File, *, library: LibImage = "opencv") -> 'ImageObject':
        bt = None
        try:
            with open(filepath.absolute(), "rb") as f:
                bt = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"{__class__.__name__} [{filepath}] not found")
        except Exception as e:
            raise Exception(f"{__class__.__name__} [{filepath}] {e}")

        if library == "pil":
            image = ImageObjectPIL(bt)
        elif library == "opencv":
            image = ImageObjectOpenCV(bt)
        else:
            raise ValueError("Biblioteca de imagem inválida.")
        return cls(image)


