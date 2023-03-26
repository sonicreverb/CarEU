import os
import pyautogui

# константы и настройка работы с пользовательским интерфейсом
pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()


# настройка конфигов прокси для wireguard
PROXY_FILENAMES = ['de2-wg-finevpn1.conf', 'de2-wg-finevpn2.conf', 'fr-wg-finevpn.conf', 'pl-wg-finevpn.conf',
                   'uk2-wg-finevpn.conf']
# todo .replace - костыль для windows в меру того, что os.path.dirname и os.path.join используют разные слэши
PROXYSTORAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'config_files').replace('/', '\\')


# установка прокси через командкую строку (заморожена из-за блокировки нетуннелированного трафкика)
def cmd_set_proxy(proxy_filename):
    print(os.path.join(PROXYSTORAGE_DIRECTORY, proxy_filename))
    os.system(f"wireguard.exe /installtunnelservice {os.path.join(PROXYSTORAGE_DIRECTORY, proxy_filename)} ")


def cmd_remove_proxy(proxy_filename):
    os.system(f"wireguard.exe /uninstalltunnelservice {proxy_filename[:-5]} ")


def cmd_run_wireguard_gui():
    os.system("wireguard.exe")


# работа с прокси через GUI
def gui_set_proxy():
    pass


def gui_remove_proxy():
    pass
    # заглушки
