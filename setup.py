from setuptools import setup, find_packages


setup(name='regerberate',
      version='0.0.1.dev',
      description='Design PCB Art with SVG Tools',
      long_description='',
      classifiers=[
          'Development Status :: 1 - Planning',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Multimedia :: Graphics',
      ],
      keywords='pcb gerber rs274x circuit svg',
      url='http://github.com/storborg/regerberate',
      author='Scott Torborg',
      author_email='storborg@gmail.com',
      install_requires=[
          'coloredlogs',
      ],
      license='MIT',
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False,
      entry_points="""\
      [console_scripts]
      regerberate = regerberate.cmd:main
      """)
