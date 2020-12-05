# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.148.1/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Option] Install Node.js
ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "source /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

COPY .devcontainer/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

# install and set zsh pure theme
ENV USER_HOME /home/vscode
RUN git clone https://github.com/sindresorhus/pure.git "$USER_HOME/.zsh/pure"
RUN echo "\nfpath+=$USER_HOME/.zsh/pure\nautoload -U promptinit; promptinit\nprompt pure" >> "$USER_HOME/.zshrc"

# install chrome for scraper
RUN mkdir -p /tmp/chrome \
   && cd /tmp/chrome \
   && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN cd /tmp/chrome \
   && ls \
   && sudo dpkg -i google-chrome*.deb || true \
   && sudo apt update \
   && sudo apt --fix-broken install -y

# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends chromium-browser
