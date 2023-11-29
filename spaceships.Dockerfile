FROM python:3.12-slim-bookworm AS builder

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

# copy the requirements file to the container
COPY requirements.txt .

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

# install the requirements
RUN pip install -r requirements.txt

# copy src/ directory to the container
COPY src/ .
RUN pip install .

FROM python:3.12-slim-bookworm AS runner

# copy the virtualenv from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
# Run the application (mount the .env file to the container or set the environment variables)
ENTRYPOINT ["spaceships-database"]

