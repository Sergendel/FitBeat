# Stage 1: Build stage installing dependencies and upgrading SQLite explicitly
FROM public.ecr.aws/lambda/python:3.11 AS build-image

RUN yum update -y \
    && yum install -y gcc make wget tar gzip

# Explicitly compile and install SQLite (3.43.2)
RUN wget https://sqlite.org/2023/sqlite-autoconf-3430200.tar.gz \
    && tar xvf sqlite-autoconf-3430200.tar.gz \
    && cd sqlite-autoconf-3430200 \
    && ./configure --prefix=/usr \
    && make \
    && make install

# Explicitly prepare Python dependencies
WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt -t ./python \
    && find ./python -name "*.pyc" -delete \
    && find ./python -type d -name "__pycache__" -exec rm -rf {} + \
    && rm -rf python/nvidia \
              python/cusparselt \
              python/triton

# Stage 2: Final runtime Lambda image explicitly
FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

# Explicitly overwrite Lambda's default SQLite library
COPY --from=build-image /usr/lib/libsqlite3.so.0 /var/lang/lib/libsqlite3.so.0
COPY --from=build-image /usr/bin/sqlite3 /usr/bin/sqlite3

# Explicitly copy Python dependencies
COPY --from=build-image /build/python ${LAMBDA_TASK_ROOT}

# Copy backend application explicitly
COPY backend ./backend

# Explicitly set Lambda handler
CMD ["backend.deployment.aws.app.lambda_handler"]
