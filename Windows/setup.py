from setuptools import setup, find_packages

setup(
    name='annefrank_injector',
    version='1.0',
    description='Windows shellcode loader with persistence features',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Excalibra/AnneFrankInjector',
    author='Excalibra',
    author_email='',
    maintainer='Excalibra',
    license='MIT',
    install_requires=['colorama', 
                      'pycryptodome'],
    py_modules=['main'],
    include_package_data=True,
    packages=find_packages(),
    package_data={'custom_certs':['cert1.pfx', 'cert2.pfx', 'osslsigncode.exe'], 
                  'templates': [
                                'stageless/*', 
                                'staged/*'
                            ]
    },
    entry_points={
        'console_scripts': [
            'annefrank-injector=main:main'
        ],
    },
    platforms=['Linux', 'Windows']
)
