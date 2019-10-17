import os
from os.path import expanduser

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch  # handling python 2.7

import pytest
from selenium import webdriver

from tests.test_cache import delete_cache
from webdriver_manager import utils
from webdriver_manager.chrome import ChromeDriverManager

PATH = '.'


def delete_old_install(path=None):
    if path is None:
        delete_cache()
    else:
        path = os.path.abspath(path)
        try:
            os.remove(os.path.join(path, 'chromedriver.exe'))
            os.remove(os.path.join(path, 'chromedriver.zip'))
        except:
            pass


def test_chrome_manager_with_specific_version():
    bin = ChromeDriverManager("2.26").install()
    assert os.path.exists(bin)


def test_chrome_manager_with_wrong_version():
    with pytest.raises(ValueError) as ex:
        delete_old_install()
        ChromeDriverManager("0.2").install()
    os_type = "win32" if utils.os_type() == "win64" else utils.os_type()
    ex_value = ("There is no such driver chromedriver with version 0.2 by "
                "http://chromedriver.storage.googleapis.com/0.2/"
                "chromedriver_{0}.zip".format(os_type))
    assert ex.value.args[0] == ex_value


def test_chrome_manager_with_selenium():
    delete_old_install()
    driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(driver_path)
    driver.get("http://automation-remarks.com")
    driver.close()


def test_chrome_manager_cached_driver_with_selenium():
    ChromeDriverManager().install()
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("http://automation-remarks.com")
    driver.close()


@pytest.mark.parametrize('os_type', ['win32', 'win64'])
def test_can_get_chrome_for_win(os_type):
    delete_cache()
    path = ChromeDriverManager(os_type=os_type).install()
    assert os.path.exists(path)


@pytest.mark.parametrize('version, driver_version',
                         [('72.0.3626', '72.0.3626.69'),
                          ('73.0.3683', '73.0.3683.68'),
                          ('74.0.3729', '74.0.3729.6')])
def test_latest_chromedriver_for_chrome(version, driver_version):
    with patch('webdriver_manager.driver.chrome_version') as chrome_version:
        chrome_version.return_value = version
        path = ChromeDriverManager().install()
        os_type = utils.os_type()
        current_os_type = "win32" if os_type == "win64" else os_type
        extension = '.exe' if os_type.startswith('win') else ''
        assert path == os.path.join(expanduser("~"), ".wdm",
                                    "chromedriver", driver_version,
                                    current_os_type,
                                    "chromedriver") + extension
