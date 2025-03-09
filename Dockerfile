# Step 1: Build the React frontend using Yarn
FROM node:20 AS frontend-build
WORKDIR /app
COPY frontend/ ./frontend/
WORKDIR /app/frontend
ARG REACT_APP_API_URL=/
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN yarn install 
RUN yarn build

# Step 2: Set up the Flask backend with Docker-in-Docker (DinD)
FROM docker:20-dind AS backend-build

WORKDIR /app
COPY backend/ ./backend/
WORKDIR /app/backend

# Install necessary dependencies
# Install necessary dependencies
RUN apk add --no-cache python3 py3-pip python3-dev \
    build-base gcc g++ musl-dev linux-headers \
    libffi-dev pkgconfig openblas-dev llvm-libomp \
    && python3 -m pip install --upgrade pip setuptools wheel


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Install IRIS Python Driver
RUN pip install ./install/intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

# Set up environment variables
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV IRIS_CONTAINER_NAME=iris-comm
ENV IRIS_IMAGE=intersystemsdc/iris-community:latest
ENV IRIS_USERNAME=demo
ENV IRIS_PASSWORD=demo

# Expose necessary ports
EXPOSE 5000 1972 52773

# Copy frontend build
WORKDIR /app
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Step 3: Start Docker-in-Docker, Run IRIS, and then Start Flask
CMD dockerd-entrypoint.sh & \
    sleep 5 && \
    docker run -d --name $IRIS_CONTAINER_NAME -p 1972:1972 -p 52773:52773 -e IRIS_USERNAME=$IRIS_USERNAME -e IRIS_PASSWORD=$IRIS_PASSWORD $IRIS_IMAGE && \
    gunicorn -b 0.0.0.0:5000 app:app
