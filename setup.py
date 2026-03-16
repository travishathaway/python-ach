from distutils.core import setup
import codecs

readme = codecs.open('README.rst', encoding='utf-8').read()

setup(
    name='ach',
    author='Travis Hathaway',
    author_email='travis.j.hathaway@gmail.com',
    version='0.2',
    packages=[
        'ach',
    ],
    url='https://github.com/travishathaway/python-ach',
    license='MIT License',
    description='Library to create and parse ACH files (NACHA)',
    long_description=readme,
)
