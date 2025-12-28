from __future__ import annotations
import threading
from typing import Any, Callable, Literal, TypeVar, TypedDict, Generic
from tkinter import (ttk, Tk, messagebox)
from digitalized.ui_core.core.observer import (
    AbstractObserver, AbstractNotifyProvider, MessageNotification, T
)
from soup_files import File, Directory, UserAppDir


def show_alert(text: str):
    messagebox.showwarning('Alerta', text)


def show_info(text: str):
    messagebox.showinfo('Info', text)


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

    def receiver_notify(self, _obj_receiver: MessageNotification[T]):
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
        self.controller_window: MyApp = master
        self._page_name: str = None
        self._page_route: str = None
        self._page_observer: ObserverWidget =  ObserverWidget()
        self._page_observer.set_page(self)
        self.frame_master: ttk.Frame = ttk.Frame(self)
        self.frame_master.pack(expand=True, fill='both', padx=1, pady=1)

    def __repr__(self):
        return f'{__class__.__name__}() {self.get_page_name()}'

    def get_observer(self) -> ObserverWidget:
        return self._page_observer

    def set_observer(self, observer: ObserverWidget):
        self._page_observer = observer
        self._page_observer.set_page(self)

    def subscribe(self, notify_provider: NotifyWidget):
        """
            Inserver-se em um objeto notificador
        """
        notify_provider.add_observer(self._page_observer)

    def set_geometry(self, geometry: str):
        self.controller_window.get_window().geometry(geometry)

    def get_page_name(self) -> str | None:
        return self._page_name

    def set_page_name(self, name: str):
        self._page_name = name

    def get_page_route(self) -> str | None:
        return self._page_route

    def set_page_route(self, route: str):
        self._page_route = route

    def receiver_notify(self, _obj: MessageNotification[T]):
        """
            Receber notificações externas de outros objetos.
        """
        print(f'{self.get_page_name()} Recebi uma notificação de : {_obj}')

    def send_notify(self, message: MessageNotification[T]):
        pass

    def init_ui_page(self):

        lb = ttk.Label(self.frame_master, text='Olá, mundo!!!')
        lb.pack()
        self.pack()

    def set_size_screen(self):
        self.controller_window.get_window().geometry('350x250')
        self.controller_window.get_window().title(f'{self.get_page_name().upper()}')

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
        self.navigator: Navigator = Navigator()
        self._base_window: BaseWindow = BaseWindow()

    def get_window(self) -> BaseWindow:
        return self._base_window

    def add_page(self, page: BasePage):
        self.navigator.add_page(page)

    def receiver_notify(self, message: MessageNotification[T]):
        self.send_notify(message)

    def send_notify(self, message: MessageNotification[T]):
        self._base_window.receiver_notify(message)

    def go_home_page(self):
        for _key in self.navigator.get_pages().keys():
            if _key == '/home':
                self.navigator.push('/home')
                break

    def exit_app(self):
        pass


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


def run_app(home_page: BasePage) -> None:
    app = MyApp()
    home_page.set_page_name('HOME PAGE')
    home_page.set_page_route('/home')
    app.add_page(home_page)
    app.navigator.push(home_page.get_page_route())
    app.get_window().mainloop()
