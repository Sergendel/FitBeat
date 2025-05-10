# Stage 1: Build stage installing dependencies
FROM public.ecr.aws/lambda/python:3.11 AS build-image

# Set working directory
WORKDIR /build

# Copy requirements and install dependencies
COPY backend/requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt -t ./python \
    && find ./python -name "*.pyc" -delete \
    && find ./python -type d -name "__pycache__" -exec rm -rf {} + \
    && rm -rf python/nvidia \
              python/cusparselt \
              python/triton \
              python/*.dist-info

# Remove unnecessary heavy packages (examples)
RUN rm -rf ./python/numpy/doc/ ./python/boto3/docs/ ./python/botocore/docs/

# Clean unnecessary cache files and binaries
RUN find ./python -name '*.pyc' -delete && \
    find ./python -name '__pycache__' -type d -exec rm -rf {} +

# Stage 2: Final stage (runtime Lambda image)
FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy dependencies from build-image
COPY --from=build-image /build/python ${LAMBDA_TASK_ROOT}

# Copy backend application code
COPY backend/ .
# COPY backend/core ./core
# COPY backend/deployment ./deployment

# Set Lambda handler
CMD ["deployment.aws.app.lambda_handler"]
