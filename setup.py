from setuptools import setup, find_packages

setup(name='swmeas',
      version='0.1.0a',
      description='Tools monitoring seawater CO2, O2 and Temp.',
      url='https://github.com/oscarbranson/swmeas',
      author='Oscar Branson',
      author_email='oscarbranson@gmail.com',
      license='MIT',
      packages=find_packages(),
      keywords=['science', 'chemistry', 'oceanography', 'carbon'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3'],
      install_requires=['pyserial>=3.3', 'LabJackPytho'],
      package_data={'swmeas': ['resources/*', 'systemd-services/*', 'rpi_scripts/*']},
      zip_safe=True)
