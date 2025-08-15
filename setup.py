from setuptools import setup, find_packages

setup(
    name='mycoCarte',
    version='0.1.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'geopandas',
        'pandas',
        'rasterio',
        'numpy',
        'scikit-learn',
        'seaborn'
    ],
    )