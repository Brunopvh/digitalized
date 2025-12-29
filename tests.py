#!/usr/bin/env python3
import sys
import os
import soup_files as sp

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'digitalized')

output_dir = sp.UserFileSystem().userDownloads.concat('output', create=True)
sys.path.insert(0, MODULES_DIR)


def test():
    from app_variacao.ui.core import run_app, MyApp

    app = MyApp()
    run_app(app)


def main():
    test()


if __name__ == '__main__':
    main()
