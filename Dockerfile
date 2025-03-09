# Step 1: Build the React frontend using Yarn
FROM node:20 AS frontend-build
WORKDIR /app
COPY frontend/ ./frontend/
WORKDIR /app/frontend
ARG REACT_APP_API_URL=/
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN yarn install 
RUN yarn build

# Step 2: Set up the Flask backend
FROM python:3.10 AS backend-build
WORKDIR /app
COPY backend/ ./backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt gunicorn
RUN pip install ./install/intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

# Step 3: Combine frontend build with backend
WORKDIR /app
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Expose port and start the app
EXPOSE 5000
WORKDIR /app/backend
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]