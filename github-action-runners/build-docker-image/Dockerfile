#1. Get the token from the code in  https://github.com/tekkies/FloHsm/settings/actions/runners/new?arch=x64&os=linux
#2. docker build --tag flohsm-build-docker-image --progress=plain --build-arg GITHUB_TOKEN=XXXXXXXXX .
#3. docker run --interactive --tty --name flohsm-build-docker-image flohsm-build-docker-image
#REMOVE CONTAINER: docker rm -f flohsm-build-docker-image

#Partsof this file based on https://testdriven.io/blog/github-actions-docker/
FROM debian:bullseye
WORKDIR actions-runner
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y libdigest-sha-perl
RUN useradd -m docker



#Based on https://github.com/tekkies/FloHsm/settings/actions/runners/new?arch=x64&os=linux
RUN curl -o actions-runner-linux-x64-2.302.1.tar.gz -L https://github.com/actions/runner/releases/download/v2.302.1/actions-runner-linux-x64-2.302.1.tar.gz
RUN echo "3d357d4da3449a3b2c644dee1cc245436c09b6e5ece3e26a05bb3025010ea14d  actions-runner-linux-x64-2.302.1.tar.gz" | shasum -a 256 -c
RUN tar xzf ./actions-runner-linux-x64-2.302.1.tar.gz
RUN ./bin/installdependencies.sh
RUN chmod --recursive 777 .
USER docker
ENV RUNNER_ALLOW_RUNASROOT=1
ARG GITHUB_TOKEN
RUN echo GITHUB_TOKEN: ${GITHUB_TOKEN}
RUN ./config.sh --url https://github.com/tekkies/FloHsm --token "${GITHUB_TOKEN}" --name flohsm-build-docker-image --labels flohsm-build-docker-image --replace

CMD ./run.sh