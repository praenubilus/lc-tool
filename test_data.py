""" Unit Tests for data.Data class
"""
import pytest
import os
from Data import Data
import config


# pytestmark = pytest.mark.timeout(5)

TEST_DATA_PATH = "test.json"
TEST_QID = str(1).zfill(config.QID_PADDING_SIZE)


@pytest.fixture(scope="function")
def dt_test():
    return Data(TEST_DATA_PATH, preload=False)


@pytest.fixture(scope="function")
def dt_default():
    return Data(preload=False)


def test_init_wo_preload_data(dt_test):
    assert dt_test.data is None


def test_init_file_path_wo_preload(dt_test):
    assert TEST_DATA_PATH == dt_test.data_file_path


def test_load_specified_data_file(dt_test):
    data = dt_test.load(TEST_DATA_PATH)
    assert dt_test.data is not None
    assert data is not None
    assert data == dt_test.data
    assert TEST_QID in data
    assert "two sum" == data[TEST_QID]["stat"]["question__title"].lower()


def test_default_init_file_path_wo_preload(dt_default):
    assert config.DATA_FILE_PATH == dt_default.data_file_path


def test_fetch_data(dt_default):
    data = dt_default.fetch()
    assert data is not None
    assert TEST_QID in data
    assert "two sum" == data[TEST_QID]["stat"]["question__title"].lower()


def test_load_default_data_file(dt_default):
    data = dt_default.load()
    assert data is None
    assert dt_default.data is None


def test_data_load_and_persistence(dt_default):
    if os.path.exists(config.DATA_FILE_PATH):
        os.remove(config.DATA_FILE_PATH)
    assert config.DATA_FILE_PATH == dt_default.data_file_path
    dt_default.load()
    assert dt_default.data is None
    dt_default.do_persistence()
    assert os.path.exists(config.DATA_FILE_PATH)
    os.remove(config.DATA_FILE_PATH)
