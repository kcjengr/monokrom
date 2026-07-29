import os
from . import monokrom_rc as monokrom_rc
import monokrom

VCP_DIR = os.path.realpath(os.path.dirname(__file__))
VCP_CONFIG_FILE = os.path.join(VCP_DIR, 'config.yml')

def main(opts=None):
    monokrom.main('plasma', opts)


if __name__ == '__main__':
    main()
