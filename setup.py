from setuptools import setup # type: ignore
import up_pps


long_description=\
'''
 ============================================================
    UP_PPS
 ============================================================
    blabla
'''

setup(name='up_pps',
      version=up_pps.__version__,
      description='up_pps',
      author='ACTOR',
      packages=['up_pps'],
      install_requires=['pip==22.3.1', 'numpy==1.24.1','ortools==9.5.2237'],
      python_requires='>=3.7'
)