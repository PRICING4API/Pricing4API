from setuptools import setup, find_packages

setup(
    name='Pricing4API',
    version='0.2.1-lightweight',
    packages=['Pricing4API', 'Pricing4API.basic', 'Pricing4API.ancillary'],
    license='MIT',
    author='Daniel Ruiz López, Ramón Gavira Sánchez',
    author_email='danruilop1@alum.us.es, rgavira@us.es',
    description='Lightweight version of Pricing4API - basic and ancillary modules only',
    install_requires=[
        # Core dependencies (reducidas al mínimo necesario)
        'numpy>=1.26.0',
        'pandas>=2.2.0',
        'matplotlib>=3.8.0',
        'PyYAML>=6.0.0',
        'python-dotenv>=1.0.0',
        # Solo si los usas en basic/ancillary
        'requests>=2.32.0',
        'httpx>=0.28.0',
    ]
)
