import threading

from app_variacao.ui_core.core import (
    BasePage, BaseWindow, MyApp, Container, ProgressBarTkIndeterminate,
    ProgressBar, ProgressBarTkDeterminate, EnumThemes, MappingStyles,
    MessageNotification
)
from tkinter import ttk
from threading import Thread


class HomePage(BasePage):

    def __init__(self, master: MyApp, **kwargs):
        super().__init__(master, **kwargs)
        self.GEOMETRY = '550x450'
        self.container_pbar: Container = Container(
            self,
            style=self.myapp_window.get_styles_mapping().get_style_pbar(),
            height=50
        )

        self.lb1 = ttk.LabelFrame(
            self.frame_master, text="Home Page"
        )
        self.lb2 = ttk.Label(
            self.frame_master, text="Olá, mundo!!!"
        )

        self._pbar_tk = ProgressBarTkDeterminate(self.container_pbar)
        self.btn = ttk.Button(
            self.frame_master,
            text='Iniciar',
            command=self.start_action,
            style=self.myapp_window.get_styles_mapping().get_style_buttons()
        )
        self.btn_stop = ttk.Button(
            self.frame_master,
            text='Stop',
            command=self.stop_action,
            style=self.myapp_window.get_styles_mapping().get_style_buttons()
        )
        self.pbar = ProgressBar(self._pbar_tk)

    def _action_start(self):
        from time import sleep
        self.pbar.set_end_value(10)
        self.pbar.start()
        for x in range(0, 10):
            self.pbar.update()
            sleep(0.2)
        self.pbar.stop()

    def start_action(self):
        my_th = threading.Thread(target=self._action_start)
        my_th.start()

    def stop_action(self):
        print('Saindo')
        self.myapp_window.exit_app()

    def init_ui_page(self):
        self.lb1.pack(padx=2, pady=2)
        self.lb2.pack(padx=2, pady=2)
        self.btn.pack(padx=2, pady=2)
        self.btn_stop.pack()
        self.pbar.set_prefix_text('Operação em andamento, aguarde...')
        self.pbar.init_pbar(
            kwargs={'theme': self.myapp_window.get_styles_mapping().get_style_pbar()},
        )
        self.pack(expand=True, fill='both', padx=2, pady=1)


class MainApp(MyApp):

    def __init__(self):
        super().__init__()

        self.main_page = HomePage(self)
        self.main_page.set_page_name('HOME')
        self.main_page.set_page_route('/home')
        self.add_page(self.main_page)


