'''Test various breakpoint operations.'''

import os
import tempfile
import pytest


def test_detect(eng, backend):
    '''Verify manual breakpoint is detected.'''
    eng.feed(backend['launch'])
    assert eng.wait_paused() is None
    eng.feed(backend['break_main'])
    eng.feed('run\n')
    assert eng.wait_signs({'cur': 'test.cpp:17', 'break': {1: [17]}}) is None


# pylint: disable=redefined-outer-name

@pytest.fixture(scope='function')
def cd_tmp():
    '''Fixture to change directory temporarily.'''
    old_dir = os.getcwd()
    os.chdir(tempfile.gettempdir())
    yield os.path.join(old_dir, 'a.out')
    os.chdir(old_dir)


def test_cd(eng, backend, cd_tmp):
    '''Verify manual breakpoint is detected from a random directory.'''
    eng.feed(backend['launchF'].format(cd_tmp))
    assert eng.wait_paused() is None
    eng.feed(backend['break_main'])
    eng.feed('run\n')
    assert eng.wait_signs({'cur': 'test.cpp:17', 'break': {1: [17]}}) is None


def test_navigate(eng, backend):
    '''Verify that breakpoints stay when source code is navigated.'''
    eng.feed(backend['launch'])
    assert eng.wait_paused() is None
    eng.feed(backend['break_bar'])
    eng.feed("<esc>:wincmd w<cr>")
    eng.feed(":e src/test.cpp\n")
    eng.feed(":10<cr>")
    eng.feed("<f8>")

    assert {'break': {1: [5, 10]}} == eng.get_signs()

    # Go to another file
    eng.feed(":e src/lib.hpp\n")
    assert {} == eng.get_signs()
    eng.feed(":8\n")
    eng.feed("<f8>")
    assert {'break': {1: [8]}} == eng.get_signs()

    # Return to the first file
    eng.feed(":e src/test.cpp\n")
    assert {'break': {1: [5, 10]}}, eng.get_signs()


def test_clear_all(eng, backend):
    '''Verify that can clear all breakpoints.'''
    eng.feed(backend['launch'])
    assert eng.wait_paused() is None
    eng.feed(backend['break_bar'])
    eng.feed(backend['break_main'])
    eng.feed("<esc>:wincmd w<cr>")
    eng.feed(":e src/test.cpp\n")
    eng.feed(":10<cr>")
    eng.feed("<f8>")

    assert {'break': {1: [5, 10, 17]}} == eng.get_signs()

    eng.feed(":GdbBreakpointClearAll\n")
    assert eng.wait_signs({}) is None


def test_duplicate(eng, backend):
    '''Verify that duplicate breakpoints are displayed distinctively.'''
    eng.feed(backend['launch'])
    assert eng.wait_paused() is None
    eng.feed(backend['break_main'])
    eng.feed('run\n')
    assert eng.wait_signs({'cur': 'test.cpp:17', 'break': {1: [17]}}) is None
    eng.feed(backend['break_main'])
    assert eng.wait_signs({'cur': 'test.cpp:17', 'break': {2: [17]}}) is None
    eng.feed(backend['break_main'])
    assert eng.wait_signs({'cur': 'test.cpp:17', 'break': {3: [17]}}) is None
    eng.feed("<esc>:wincmd w<cr>")
    eng.feed(":17<cr>")
    eng.feed("<f8>")
    assert eng.wait_signs({'cur': 'test.cpp:17', 'break': {2: [17]}}) is None
    eng.feed("<f8>")
    assert eng.wait_signs({'cur': 'test.cpp:17', 'break': {1: [17]}}) is None
    eng.feed("<f8>")
    assert eng.wait_signs({'cur': 'test.cpp:17'}) is None
