#!/usr/bin/env python3
import sys
import os
import soup_files as sp

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')

output_dir = sp.UserFileSystem().userDownloads.concat('output', create=True)
sys.path.insert(0, MODULES_DIR)


def test():
    from digitalized.ui_core.core.__init__ import (
        BasePage, NotifyWidget, MyApp, run_app
    )

    app = MyApp()
    page = BasePage(app)
    page.set_page_name('HOME')
    page.set_page_route('/home')
    app.add_page(page)
    app.navigator.push(page.get_page_route())

    _notif = NotifyWidget()
    page.subscribe(_notif)
    _notif.send_notify()
    app.get_window().mainloop()


def main():
    test()


if __name__ == '__main__':
    main()
