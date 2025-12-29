from __future__ import annotations
import threading
from abc import ABC, abstractmethod
from enum import StrEnum
from tkinter import ttk, Tk
from typing import Any, Callable, Literal, TypeVar, TypedDict, Generic
from tkinter import (ttk, Tk, messagebox)
from app_variacao.ui.core.base_types import (
    AbstractObserver, AbstractNotifyProvider,
    MessageNotification, T, CoreDict
)
from soup_files import File, Directory, UserAppDir


def show_alert(text: str):
    messagebox.showwarning('Alerta', text)


def show_info(text: str):
    messagebox.showinfo('Info', text)


#=================================================================#
# Temas e Estilos
#=================================================================#

class EnumThemes(StrEnum):
    # Tema dos Frames
    DARK = 'Black.TFrame'
    LIGHT = 'LightFrame.TFrame'
    DARK_PURPLE = 'DarkPurple.TFrame'
    LIGHT_PURPLE = 'LightPurple.TFrame'
    GRAY = 'CinzaFrame.TFrame'
    # Tama dos botões
    BUTTON_PURPLE_LIGHT = 'Custom.TButtonPurpleLight'
    BUTTON_GREEN = 'Custom.TButtonGreen'
    # Tema da barra de progresso
    PBAR_GREEN = "Custom.Horizontal.TProgressbar"
    PBAR_PURPLE_LIGHT = "Thin.Horizontal.TProgressbar"
    PBAR_PURPLE = "Purple.Horizontal.TProgressbar"


class AppStyles(object):

    def __init__(self, window: Tk):
        self.root_window = window
        self.root_style = ttk.Style(self.root_window)
        self.PADDING_BTN = (6, 8)
        self.WIDTH_BTN = 13

        # ==============================================================#
        # Estilo para os Frames
        # ==============================================================#
        # Estilo "LightFrame"
        self.styleLight = ttk.Style(self.root_window)
        self.styleLight.configure(
            "LightFrame.TFrame",
            background="white",
            relief="solid",
            borderwidth=1
        )
        # Estilo "CinzaFrame.TFrame"
        self.styleGray = ttk.Style(self.root_window)
        self.styleGray.configure(
            "CinzaFrame.TFrame",
            background="lightgray",
            relief="solid",
            borderwidth=1
        )
        # Estilo "Black.TFrame"
        self.styleFrameBlack = ttk.Style(self.root_window)
        self.styleFrameBlack.theme_use("default")
        self.styleFrameBlack.configure(
            "Black.TFrame",
            background="#2C2C2C"
        )  # Cor de fundo preto
        # Estilo LightPurple.TFrame - Fundo Roxo Claro
        self.styleFrameLightPurple = ttk.Style(self.root_window)
        self.styleFrameLightPurple.theme_use("default")
        self.styleFrameLightPurple.configure(
            "LightPurple.TFrame",  # Nome do estilo alterado
            background="#9370DB"  # Roxo claro (MediumPurple)
        )
        # Estilo DarkPurple.TFrame Fundo Roxo Escuro
        self.styleFrameDarkPurple = ttk.Style(self.root_window)
        self.styleFrameDarkPurple.theme_use("default")
        self.styleFrameDarkPurple.configure(
            "DarkPurple.TFrame",
            background="#4B0082"  # Roxo escuro
        )
        # Estilo para Frame
        self.styleFrameDarkGray = ttk.Style(self.root_window)
        self.styleFrameDarkGray.theme_use("default")
        self.styleFrameDarkGray.configure(
            "DarkGray.TFrame",  # Nome do estilo alterado
            background="#2F4F4F"  # Cinza escuro (DarkSlateGray)
        )
        # # Estilo para Frame
        self.styleFrameDarkOrange = ttk.Style(self.root_window)
        self.styleFrameDarkOrange.theme_use("default")
        self.styleFrameDarkOrange.configure(
            "DarkOrange.TFrame",  # Nome do estilo alterado
            background="#FF8C00"  # Laranja escuro (DarkOrange)
        )
        # ==============================================================#
        # Estilo para os botões
        # ==============================================================#
        # Roxo Claro
        self.styleButtonPurpleLight = ttk.Style(self.root_window)
        self.styleButtonPurpleLight.theme_use("default")
        self.styleButtonPurpleLight.layout(
            "Custom.TButtonPurpleLight",
            self.styleButtonPurpleLight.layout("TButton")
        )
        # Define o estilo do botão roxo claro
        self.styleButtonPurpleLight.configure(
            "Custom.TButtonPurpleLight",
            foreground="white",
            background="#B388EB",  # Roxo claro
            borderwidth=1,
            focusthickness=3,
            focuscolor='none',
            anchor='center',
            padding=self.PADDING_BTN,
            width=self.WIDTH_BTN,
        )
        self.styleButtonPurpleLight.map(
            "Custom.TButtonPurpleLight",
            background=[("active", "#a070d6"), ("pressed", "#8b5fc0")]
        )
        # Verde
        self.styleButtonGreen = ttk.Style(self.root_window)
        self.styleButtonGreen.theme_use("default")
        self.styleButtonGreen.layout(
            "Custom.TButtonGreen",
            self.styleButtonGreen.layout("TButton")
        )
        # Define o estilo do botão verde
        self.styleButtonGreen.configure(
            "Custom.TButtonGreen",
            foreground="white",
            background="#5cb85c",  # Verde
            borderwidth=1,
            focusthickness=3,
            focuscolor='none',
            anchor='center',
            padding=self.PADDING_BTN,
            width=self.WIDTH_BTN,
        )
        self.styleButtonGreen.map(
            "Custom.TButtonGreen",
            background=[("active", "#4cae4c"), ("pressed", "#449d44")]
        )

        # ==============================================================#
        # Estilo para Labels
        # ==============================================================#
        self.styleLabelPurple = ttk.Style(self.root_window)
        self.styleLabelPurple.configure(
            "LargeFont.TLabel",  # Nome do estilo
            font=("Helvetica", 14),  # Fonte maior
            background="#9370DB",  # Cor de fundo roxo claro
            foreground="white"  # Cor do texto branco
        )
        # Default
        self.styleLabelDefault = ttk.Style(self.root_window)
        self.styleLabelDefault.configure(
            "BoldLargeFont.TLabel",  # Nome do estilo
            font=("Helvetica", 14, "bold")  # Fonte maior e negrito
        )

        # ==============================================================#
        # Estilo para Barra de progresso
        # ==============================================================#
        # Verde
        self.stylePbarGreen = ttk.Style(self.root_window)
        self.stylePbarGreen.theme_use('default')
        # Define o novo estilo
        self.stylePbarGreen.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#f0f0f0',  # cor de fundo da barra
            background='#4CAF50',  # cor da barra de progresso
            thickness=6,  # espessura da barra
            bordercolor='#cccccc',  # borda
            lightcolor='#4CAF50',  # brilho da barra
            darkcolor='#4CAF50',  # sombra da barra
        )
        # Barra de progresso Roxo claro
        self.stylePbarPurpleLight = ttk.Style(self.root_window)
        self.stylePbarPurpleLight.theme_use('default')
        self.stylePbarPurpleLight.configure(
            "Thin.Horizontal.TProgressbar",
            thickness=6,  # altura fina
            troughcolor="#eeeeee",  # fundo da barra
            background="#D19FE8"  # roxo claro
            )
        # Barra de progresso Roxo escuro
        self.stylePbarPurple = ttk.Style(self.root_window)
        self.stylePbarPurple.theme_use('default')
        self.stylePbarPurple.configure(
            "Purple.Horizontal.TProgressbar",
           thickness=6,  # altura fina
           troughcolor="#eeeeee",  # fundo da barra
           background="#4B0081"
           )

    def get_styles(self) -> MappingStyles:
        return MappingStyles(
            {
                'buttons': EnumThemes.BUTTON_PURPLE_LIGHT,
                'labels': "LargeFont.TLabel",
                'frames': EnumThemes.DARK,
                'pbar': EnumThemes.PBAR_PURPLE,
            }
        )


class MappingStyles(CoreDict[str]):

    _instance_map_styles = None

    def __new__(cls, *args, **kwargs):
        if cls._instance_map_styles is None:
            cls._instance_map_styles = super(MappingStyles, cls).__new__(cls)
        return cls._instance_map_styles

    def __init__(self, values: dict[str, str] = None) -> None:
        super().__init__(values)
        # Garante que __init__ não será executado mais de uma vez
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self._observers: list[AbstractObserver] = list()
        self._message = MessageNotification({'provider': self})

    def add_observer(self, obs: AbstractObserver) -> None:
        self._observers.append(obs)

    def send_notify(self):
        for obs in self._observers:
            obs.receiver_notify(self._message)

    def get_style_buttons(self) -> str:
        return self['buttons']

    def set_style_buttons(self, style: str) -> None:
        self['buttons'] = style

    def get_style_labels(self) -> str:
        return self['labels']

    def set_style_labels(self, style: str) -> None:
        self['labels'] = style

    def get_style_frames(self) -> str:
        return self['frames']

    def set_style_frames(self, style: str) -> None:
        self['frames'] = style

    def get_style_pbar(self) -> str:
        return self['pbar']

    def set_style_pbar(self, style: str) -> None:
        self['pbar'] = style


class ObserverWidget(AbstractObserver):

    def __init__(self):
        super().__init__()
        self._page: BasePage = None

    def __repr__(self):
        return f'{self.__class__.__name__}() Sujeito Observador'

    def set_page(self, page: BasePage):
        self._page = page

    def receiver_notify(self, _obj_receiver: MessageNotification[T]):
        if self._page is not None:
            self._page.receiver_notify(_obj_receiver)


class NotifyWidget(AbstractNotifyProvider):

    def __init__(self):
        super().__init__()
        self._name = 'window_notify'

    def __repr__(self):
        return f'{__class__.__name__}() Sujeito Notificador'

    def send_notify(self, message: MessageNotification[T] = None):
        if message is None:
            message = MessageNotification()
            message['provider'] = self
        if not 'provider' in message.keys():
            message['provider'] = self

        for _observer in self.observer_list:
            _observer.receiver_notify(message)


class BaseWindow(Tk):

    def __init__(
                self, screenName=None, baseName=None,
                className="Tk", useTk=True, sync=False, use=None
            ):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.fun_alert: Callable[[str], None] = show_alert
        self.fun_info: Callable[[str], None] = show_info
        self.geometry('500x320')

    def receiver_notify(self, message: MessageNotification[T]):
        pass

    def initUI(self) -> None:
        pass

    def set_theme(self, app_them: Any) -> None:
        pass

    def show_alert(self, text: str):
        #messagebox.showinfo('Alerta', text)
        self.fun_alert(text)

    def show_info(self, text: str):
        self.fun_info(text)

    def _exit_threads(self) -> None:
        pass

    def exit_app(self):
        """
        Sai do programa
        """
        self._exit_threads()
        print("Encerrando GUI.")
        self.quit()


class Container(ttk.Frame):

    def __init__(
                self, master=None, *, border=None,
                borderwidth=None, class_="", cursor="",
                height=25, name=None, padding=None, relief=None,
                style="", takefocus="", width=0
            ):
        super().__init__(
                master, border=border, borderwidth=borderwidth, class_=class_,
                cursor=cursor, height=height, name=name, padding=padding,
                relief=relief, style=style, takefocus=takefocus, width=width
            )


class ContainerH(Container):

    def __init__(
                self, master=None, *, border=None,
                borderwidth=None, class_="", cursor="",
                height=0, name=None, padding=None, relief=None,
                style="", takefocus="", width=0
            ):
        super().__init__(
                master, border=border, borderwidth=borderwidth, class_=class_,
                cursor=cursor, height=height, name=name, padding=padding,
                relief=relief, style=style, takefocus=takefocus, width=width
            )
        pass


class ContainerV(ttk.Frame):

    def __init__(
                self, master=None, *, border=None,
                borderwidth=None, class_="", cursor="",
                height=0, name=None, padding=None, relief=None,
                style="", takefocus="", width=0
            ):
        super().__init__(
                master, border=border, borderwidth=borderwidth, class_=class_,
                cursor=cursor, height=height, name=name, padding=padding,
                relief=relief, style=style, takefocus=takefocus, width=width
            )
        pass


class BasePage(ttk.Frame):

    def __init__(
                self, master: MyApp, *, border=None,
                borderwidth=None, class_="", cursor="",
                height=0, name=None, padding=None,
                relief=None, style="", takefocus="",
                width=0,
                **kwargs,
            ):
        super().__init__(
                    master.get_window(), border=border, borderwidth=borderwidth,
                    class_=class_, cursor=cursor, height=height,
                    name=name, padding=padding, relief=relief,
                    style=style, takefocus=takefocus,
                    width=width
            )
        self.myapp_window: MyApp = master
        self._page_name: str = None
        self._page_route: str = None
        self._page_observer: ObserverWidget = ObserverWidget()
        self._page_observer.set_page(self)
        self.frame_master: ttk.Frame = ttk.Frame(
            self,
            style=self.myapp_window.get_styles_mapping().get_style_frames(),
        )
        self.frame_master.pack(expand=True, fill='both', padx=1, pady=1)
        self.GEOMETRY: str = '350x250'

    def __repr__(self):
        return f'{__class__.__name__}() {self.get_page_name()}'

    def get_observer(self) -> ObserverWidget:
        return self._page_observer

    def set_observer(self, obs: ObserverWidget):
        self._page_observer = obs
        self._page_observer.set_page(self)

    def subscribe(self, notify_provider: NotifyWidget):
        """
            Inserver-se em um objeto notificador
        """
        notify_provider.add_observer(self._page_observer)

    def set_geometry(self, geometry: str):
        self.myapp_window.get_window().geometry(geometry)

    def get_page_name(self) -> str | None:
        return self._page_name

    def set_page_name(self, name: str):
        self._page_name = name

    def get_page_route(self) -> str | None:
        return self._page_route

    def set_page_route(self, route: str):
        self._page_route = route

    def receiver_notify(self, _obj: MessageNotification):
        """
            Receber notificações externas de outros objetos.
        """
        print(f'{self.get_page_name()} Recebi uma notificação de : {_obj}')
        if isinstance(_obj['provider'], MappingStyles):
            print(f'{self.get_page_name()} Alterando o tema!')

    def send_notify(self, message: MessageNotification):
        pass

    def init_ui_page(self):
        pass

    def set_size_screen(self):
        self.myapp_window.get_window().geometry(self.GEOMETRY)
        self.myapp_window.get_window().title(f'{self.get_page_name().upper()}')

    def update_page_state(self):
        pass


class MyApp(object):
    """
        Controlador de páginas
    """
    _instance_controller = None

    def __new__(cls, *args, **kwargs):
        if cls._instance_controller is None:
            cls._instance_controller = super(MyApp, cls).__new__(cls)
        return cls._instance_controller

    def __init__(self):
        super().__init__()
        # Garante que __init__ não será executado mais de uma vez
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self._navigator: Navigator = Navigator()
        self._base_window: BaseWindow = BaseWindow()
        self._styles_app = AppStyles(self._base_window)
        self._styles_mapping = self._styles_app.get_styles()

    def get_styles_app(self) -> AppStyles:
        return self._styles_app

    def get_styles_mapping(self) -> MappingStyles:
        return self._styles_mapping

    def get_navigator(self) -> Navigator:
        return self._navigator

    def get_pages(self) -> dict[str, BasePage]:
        return self._navigator.get_pages()

    def get_window(self) -> BaseWindow:
        return self._base_window

    def add_page(self, page: BasePage):
        """
        Adiciona uma página ao navegador de páginas
        """
        # Inscrever a página no objeto notificador MappingStyes() para
        # receber notificações de atualização de temas/estilos
        self.get_styles_mapping().add_observer(page.get_observer())  # Cada página tem um observador principal
        self._navigator.add_page(page)

    def receiver_notify(self, message: MessageNotification[T]):
        self.send_notify(message)

    def send_notify(self, message: MessageNotification[T]):
        self._base_window.receiver_notify(message)

    def go_home_page(self):
        for _key in self._navigator.get_pages().keys():
            if _key == '/home':
                self._navigator.push('/home')
                break

    def exit_app(self):
        self._base_window.exit_app()


class Navigator(object):

    _instance_navigator = None

    def __new__(cls, *args, **kwargs):
        if cls._instance_navigator is None:
            cls._instance_navigator = super(Navigator, cls).__new__(cls)
        return cls._instance_navigator

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self._app_pages: dict[str, BasePage] = dict()
        self.current_page: BasePage = None  # Página atualmente exibida
        self.history_pages: list[str] = list()  # Pilha para armazenar o histórico de navegação

    def get_pages_route(self) -> list[str]:
        return list(self._app_pages.keys())

    def add_page(self, page: BasePage):
        if page.get_page_route() is None:
            raise ValueError(f'Defina uma rota para página: {page}')
        if page.get_page_route() in self.get_pages_route():
            return
        self._app_pages[page.get_page_route()] = page
        print(f'Página adicionada: {page.get_page_route()}')

    def get_pages(self) -> dict[str, BasePage]:
        return self._app_pages

    def push(self, page_route: str):
        """
        Exibe a página especificada.

        :param page_route: Rota da página a ser exibida.
        """
        if not (page_route in self.get_pages_route()):
            messagebox.showwarning(
                "Aviso", f'Página não encontrada: {page_route}'
            )
            return

        # Esconde a página atual, se houver
        if self.current_page is not None:
            self.history_pages.append(self.current_page.get_page_route())  # Salvar no histórico
            self.current_page.pack_forget()

        # Mostra a nova página
        self.current_page = self._app_pages[page_route]
        self.current_page.set_size_screen()
        self.current_page.update_page_state()
        self.current_page.init_ui_page()
        self.current_page.pack(expand=True, fill='both', padx=2, pady=2)

    def pop(self):
        """
        Retorna à página anterior no histórico de navegação.
        """
        if len(self.history_pages) == 0:
            messagebox.showwarning(
                "Aviso", "Não há páginas anteriores no histórico para retornar."
            )
            return

        # Esconde a página atual
        if self.current_page is not None:
            self.current_page.pack_forget()

        # Recupera a página anterior do histórico
        previous_page_route: str = self.history_pages.pop()
        self.current_page = self._app_pages[previous_page_route]
        self.current_page.init_ui_page()
        self.current_page.set_size_screen()
        self.current_page.update_page_state()
        self.current_page.pack(expand=True, fill='both', padx=2, pady=2)


class InterfaceProgressBar(ABC):

    def __init__(self):
        self._current_percent: float = 0.0  # 0 -> 100
        self._initial_value: int = 0
        self._end_value: int = 0
        self._prefix_text: str = '-'
        self._output_text: str = 'Aguarde...'
        self._running: bool = False

    @abstractmethod
    def start(self):
        """Inicia a barra de progresso (pode ser vazio dependendo da implementação)"""
        pass

    @abstractmethod
    def stop(self):
        """Para a barra de progresso (pode ser vazio dependendo da implementação)"""
        pass

    @abstractmethod
    def update_output_text(self):
        pass

    @abstractmethod
    def init_pbar(self, **kwargs):
        pass

    @abstractmethod
    def get_real_pbar(self) -> Any:
        pass

    def is_running(self) -> bool:
        return self._running

    def set_running(self, running: bool):
        self._running = running

    def get_prefix_text(self) -> str:
        return self._prefix_text

    def set_prefix_text(self, text: str) -> None:
        self._prefix_text = text

    def add_count_value(self) -> None:
        if self._initial_value < self._end_value:
            self._initial_value += 1

    def calcule_current_progress(self) -> None:
        if self._current_percent < 0:
            self._current_percent = 0.0
            return
        if self._initial_value >= self._end_value:
            self._current_percent = 100.0
            self._initial_value = self._end_value
        if self._end_value < 0:
            print(f'DEBUG: {__class__.__name__} Erro ... defina um valor final diferente de 0')
            return
        self._current_percent = (self._initial_value / self._end_value) * 100
        self.set_output_text(
            f"{self._current_percent:.2f}% [{self._initial_value}/{self._end_value}]:"
        )

    def set_output_text(self, text: str):
        self._output_text = text

    def get_output_text(self):
        return self._output_text

    def get_message_text(self) -> str:
        return f"{self.get_output_text()} {self.get_prefix_text()}"

    def set_current_percent(self, prog: float):
        self._current_percent = prog

    def get_current_percent(self) -> float:
        return self._current_percent

    def set_initial_value(self, prog: int):
        self._initial_value = prog

    def get_initial_value(self) -> int:
        return self._initial_value

    def set_end_value(self, prog: int):
        self._end_value = prog

    def get_end_value(self) -> int:
        return self._end_value


class ProgressBarTkIndeterminate(InterfaceProgressBar):

    def __init__(self, container: Container):
        super().__init__()
        self._container: Container = container
        self._lb_text = ttk.Label(self._container, text='-')
        self._real_pbar: ttk.Progressbar = ttk.Progressbar(
            self._container, mode='indeterminate'
        )

    def get_real_pbar(self) -> ttk.Progressbar:
        return self._real_pbar

    def init_pbar(self, **kwargs):
        self._lb_text.pack(expand=True, fill='both')
        self._container.pack(expand=True, fill='x', padx=1, pady=1)
        self._real_pbar.pack(expand=True, fill='x', padx=1, pady=1)

    def start(self):
        self._real_pbar.start(8)

    def stop(self):
        self.add_count_value()
        self.calcule_current_progress()
        self.update_output_text()
        self._real_pbar.stop()

    def update_output_text(self):
        self._lb_text.configure(text=self.get_message_text())


class ProgressBarTkDeterminate(InterfaceProgressBar):

    def __init__(self, container: Container):
        super().__init__()
        self._container: Container = container
        self._lb_text = ttk.Label(self._container, text='-')
        self._real_pbar: ttk.Progressbar = ttk.Progressbar(
            self._container, mode='determinate', maximum=100
        )

    def get_real_pbar(self) -> ttk.Progressbar:
        return self._real_pbar

    def init_pbar(self, **kwargs):
        self._container.configure(height=35)
        # self._container.pack_propagate(False)
        #self._container.pack(fill='x', padx=2, pady=2)
        self._container.pack(side='bottom', fill='x', padx=2, pady=1)
        self._lb_text.pack(fill='x', padx=2, pady=1)
        if kwargs:
            if 'style' in kwargs:
                self._real_pbar.configure(style=kwargs['style'])
        self._real_pbar.pack(expand=True, fill='x', padx=2, pady=1)

    def start(self):
        self.set_running(True)
        self._real_pbar['value'] = 0

    def stop(self):
        self.add_count_value()
        self.calcule_current_progress()
        self.update_output_text()
        self._real_pbar.stop()
        self.set_running(False)

    def update_output_text(self):
        self._lb_text.configure(text=self.get_message_text())
        self._real_pbar['value'] = self.get_current_percent()
        # FORÇA o Tkinter a redesenhar a interface imediatamente
        self._container.update_idletasks()


class ProgressBar(object):

    def __init__(self, pbar: InterfaceProgressBar):
        super().__init__()
        self.interface_pbar: InterfaceProgressBar = pbar

    def get_real_pbar(self) -> Any:
        self.interface_pbar.get_real_pbar()

    def init_pbar(self, **kwargs):
        self.interface_pbar.init_pbar(**kwargs)

    def get_message_text(self) -> str:
        return self.interface_pbar.get_message_text()

    def update_output_text(self):
        self.interface_pbar.update_output_text()

    def update(self, value_progress: int = None, output_text: str = None):
        _increment = True if value_progress is None else False
        if value_progress is not None:
            self.set_initial_value(value_progress)
        if output_text is not None:
            self.set_output_text(output_text)
        if _increment:
            self.add_count_value()
        self.calcule_current_progress()
        self.update_output_text()

    def start(self):
        self.interface_pbar.start()

    def stop(self):
        self.interface_pbar.stop()

    def is_running(self) -> bool:
        return self.interface_pbar.is_running()

    def set_running(self, running: bool):
        self.interface_pbar.set_running(running)

    def get_prefix_text(self) -> str:
        return self.interface_pbar.get_prefix_text()

    def set_prefix_text(self, text: str) -> None:
        self.interface_pbar.set_prefix_text(text)

    def add_count_value(self) -> None:
        self.interface_pbar.add_count_value()

    def calcule_current_progress(self) -> None:
        self.interface_pbar.calcule_current_progress()

    def set_output_text(self, text: str):
        self.interface_pbar.set_output_text(text)

    def get_output_text(self):
        return self.interface_pbar.get_output_text()

    def set_current_percent(self, prog: float):
        self.interface_pbar.set_current_percent(prog)

    def get_current_percent(self) -> float:
        return self.interface_pbar.get_current_percent()

    def set_initial_value(self, prog: int):
        self.interface_pbar.set_initial_value(prog)

    def get_initial_value(self) -> int:
        return self.interface_pbar.get_initial_value()

    def set_end_value(self, prog: int):
        self.interface_pbar.set_end_value(prog)

    def get_end_value(self) -> int:
        return self.interface_pbar.get_end_value()


def run_app(myapp: MyApp) -> None:
    myapp.get_navigator().push('/home')
    myapp.get_window().mainloop()
