# import os, sys
# import re
# import shutil
import subprocess

# from config import config
# from file_operations import File

# import io


# fs = File()

# from utils import get_filesize, getHumanReadableFilesize, get_dir_size

import subprocess

# if Config.PRODUCTION or Config.TESTING_MODE:
#     path_pngquant_binary = 'pngquant'
# else:
#     path_pngquant_binary = u'%s/src/banner_processor/pngquant_macos_binary/pngquant' % Config.BASE_DIR


path_pngquant_binary = "pngquant"


class PNGOptimizer:
    # Initializer / Instance Attributes
    def __init__(self):
        self.bitmaps = []

    def optimize_PNG(self, path_src, path_dest):
        # ./pngquant --quality 50-80 original.png --ext _opt.png

        # print('> optimize_PNG')
        args = [path_pngquant_binary, "--quality", "50-80", "--force", path_src, "--output", path_dest]
        # print ('executing ' + ' '.join(args))
        subprocess.call(args)
