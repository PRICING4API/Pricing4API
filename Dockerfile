FROM jupyter/minimal-notebook:python-3.9
# Set the working directory in the container
WORKDIR work

# Copy the dependencies file to the working directory
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir dist/Pricing4API-0.2.1.tar.gz 





