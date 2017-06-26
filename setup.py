from setuptools import setup, find_packages

setup(name='cbsyst',
      version='0.0.1',
      description='Tools monitoring seawater CO2, pH and Temp.',
      url='https://github.com/oscarbranson/swmeas',
      author='Oscar Branson',
      author_email='oscarbranson@gmail.com',
      license='MIT',
      packages=find_packages(),
      keywords=['science', 'chemistry', 'oceanography', 'carbon'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 2',
                   ],
      install_requires=['numpy',],
      zip_safe=True)
