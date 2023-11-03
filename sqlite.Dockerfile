FROM debian:bookworm-slim

# install sqlite3 from source
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y sqlite3

CMD ["sqlite3", "--version"]