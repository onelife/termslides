# -*- coding: utf-8 -*-

import sys
import pytest


@pytest.fixture(scope='class')
def setup(request):
    print('\n')
    print('##################################################')
    print('###                Start test                 ####')
    print('##################################################')

    print('\n')
    print('0. Prepare')
    print('#' * 50)

    sys.path.append('../')
    # setattr(request.cls, 'xxx', xxx)

    yield

    # xxx.yyy()

    print('\n')
    print('##################################################')
    print('###                 Test end                  ####')
    print('##################################################')
    print('\n')


@pytest.mark.usefixtures('setup')
class TestImport(object):
    # xxx = None

    def test_import(self):
        print('\n')
        print('1. Import module')
        print('#' * 50)

        from termslides import termslides