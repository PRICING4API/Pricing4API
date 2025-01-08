# Usar una imagen base de Jupyter con Python 3.10
FROM jupyter/base-notebook:python-3.10.11

# Establecer el directorio de trabajo
WORKDIR /home/jovyan/work

COPY Pricing4API /home/jovyan/work/Pricing4API
COPY setup.py /home/jovyan/work/setup.py

# Instalar la librería en modo editable
RUN pip install -e /home/jovyan/work

# Copiar los notebook al contenedor
COPY notebooks /home/jovyan/work/notebooks

# Exponer el puerto 8888 para Jupyter
EXPOSE 8888

# Comando para iniciar JupyterLab sin token
CMD ["start.sh", "jupyter", "lab", "--LabApp.token=''"]