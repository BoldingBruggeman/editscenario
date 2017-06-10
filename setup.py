from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='editscenario',
      version='0.1',
      description='Generate Fortran namelists from XML-files',
      long_description=readme(),
      url='http://github.com/BoldingBruggeman/editscenario',
      author='Jorn Bruggeman',
      author_email='jorn@bolding-bruggeman.com',
      license='GPL',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Numerical Models :: Configuration Tools',
          'License :: OSI Approved :: GPL License',
          'Programming Language :: Python :: 2.7',
      ],
      entry_points={
          'console_scripts': [
                'editscenario=editscenario.editscenario:main',
                'nml2xml=editscenario.nml2xml:main',
          ]
      },
      packages=['editscenario'],
#      packages=find_packages(exclude=['bin']),
      include_package_data=True,
      zip_safe=False)
