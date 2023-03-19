import os


PROXY_FILENAMES = ['de2-wg-finevpn1.conf', 'de2-wg-finevpn2.conf', 'fr-wg-finevpn.conf', 'pl-wg-finevpn.conf',
                   'uk2-wg-finevpn.conf']
# todo .replace - костыль для windows в меру того, что os.path.dirname и os.path.join используют разные слэши
PROXYSTORAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'config_files').replace('/', '\\')


def set_proxy(proxy_filename):
    print(os.path.join(PROXYSTORAGE_DIRECTORY, proxy_filename))
    os.system(f"wireguard.exe /installtunnelservice {os.path.join(PROXYSTORAGE_DIRECTORY, proxy_filename)} ")


def remove_proxy(proxy_filename):
    os.system(f"wireguard.exe /uninstalltunnelservice {proxy_filename[:-5]} ")
