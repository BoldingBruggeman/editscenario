from setuptools import setup

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
      scripts=['bin/editscenario.py', 'bin/nml2xml.py'],
#      packages=['editscenario'],
      include_package_data=True,
      zip_safe=False)
