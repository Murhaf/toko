import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


osname = os.uname()[0]

toko_data_files= [('models', ['models/ptb.model']),
                  ('data', ['etc/data/test.raw'])]

toko_entry_points = {'console_scripts': ['toko=toko.toko:main'],}

def readme():
    with open('README.md') as f:
        return f.read()

if osname == "Linux":
    config = {
        'description': 'ML-based Tokenization',
        'long_description': readme(),
        'author': 'murhaff',
        'url': 'https://github.com/Murhaf/toko',
        'download_url': 'https://github.com/Murhaf/toko',
        'author_email': 'murhaff@ifi.uio.no',
        'version': '0.1.0',
        #'install_requires': ['argparse'],
        'packages': find_packages(),
        'data_files' : toko_data_files,
        'include_package_data' : True,
        #'package_data' : toko_package_data,
        'name': 'toko',
        'entry_points': toko_entry_points,
        'zip_safe' : False
        }


setup(**config)
