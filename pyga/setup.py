from setuptools import setup
import pyga
import re
def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)
    
    return requirements

def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
    
    return dependency_links


setup(name='pyga',
      version=pyga.__version__,
      author='Alexey Strelkov',
      author_email='datagreed@gmail.com',
      url='https://bitbucket.org/DataGreed/pyga/',
      license='MIT',
      packages=['pyga'],
      install_requires = parse_requirements('requirements.txt'),
      dependency_links = parse_dependency_links('requirements.txt'),
      long_description="Let's you use google analytics tracking from your python scripts. Solutions for Flask and Django provided out-of-the-box"
      )