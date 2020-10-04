from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='editscenario',
      version='0.11.7',
      description='Generate Fortran namelists from XML-files',
      long_description=readme(),
      url='http://github.com/BoldingBruggeman/editscenario',
      author='Jorn Bruggeman',
      author_email='jorn@bolding-bruggeman.com',
      license='GPL',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Programming Language :: Python :: 2 :: Only',
      ],
      entry_points={
          'console_scripts': [
                'editscenario=editscenario.editscenario:main',
                'nml2xml=editscenario.nml2xml:main',
          ]
      },
      packages=['editscenario'],
#      packages=find_packages(exclude=['bin']),
      install_requires=['xmlstore>=0.9.9'],
      include_package_data=True,
      zip_safe=False)
