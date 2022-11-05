ARG BUILD_CHAIN_ADDRESS_DB=copy

FROM alpine as build_copy
ONBUILD COPY file /file

FROM alpine as build_no_copy
ONBUILD RUN echo "I don't copy"

FROM build_${BUILD_ENV}

FROM python:3.10

# Get some bash tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        git \
        openssh-client \
        sqlite3 \
        wget

# Pull some wallet tag sources of variable quality from github (GIT_REPO_DIR comes from .env)
ENV CHAIN_ADDRESS_DATA_DIR=/chain_address_data
RUN mkdir ${CHAIN_ADDRESS_DATA_DIR}
WORKDIR ${CHAIN_ADDRESS_DATA_DIR}

# Pull Adamant vaults and other chain address data that is not in the chain_address DB yet.
RUN git clone https://github.com/eepdev/vaults.git && \
    git clone https://github.com/rchen8/hop-airdrop.git && \
    git clone https://github.com/Mmoouu/test-iotxview/ && \
    git clone https://github.com/hylsceptic/ethereum_parser.git && \
    git clone https://github.com/yaocg/uniswap-arbitrage.git && \
    git clone https://github.com/m-root/arb-trading.git && \
    git clone https://github.com/Inka-Finance/assets.git && \
    git clone https://github.com/aurafinance/aura-token-allocation.git && \
    git clone https://github.com/kovart/forta-agents.git && \
    git clone https://github.com/graphsense/graphsense-tagpacks.git && \
    git clone https://github.com/oushu1zhangxiangxuan1/TronStreaming.git

# Remove some unnecessary cruft from image
RUN rm -fr test-iotxview/.git && find test-iotxview/ -name '*.png' -delete && \
    rm -fr assets/.git && find assets/ -name '*.png' -delete && \
    rm -fr TronStreaming/.git

# Python env vars
ARG PYTHON_DIR=/python
WORKDIR ${PYTHON_DIR}
ENV ETHECYCLE_ENV=development \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="${PYTHON_DIR}/poetry" \
    POETRY_NO_INTERACTION=1

# Install poetry. Lots of ideas as to how to approach this here: https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker
COPY poetry.lock pyproject.toml ${PYTHON_DIR}/
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
RUN poetry config virtualenvs.create false && \
    poetry install $(test "$ETHECYCLE_ENV" == production && echo "--no-dev")

# TODO: Put a temporary copy of repo on the image and bake the chain addresses database into the image
ARG ETHECYCLE_TMP_DIR_FOR_BUILDING_CHAIN_ADDRESS_DB=/ethecycle_build_address_db
WORKDIR ${ETHECYCLE_TMP_DIR_FOR_BUILDING_CHAIN_ADDRESS_DB}
COPY ./ ./
RUN IS_DOCKER_IMAGE_BUILD=True ./import_chain_addresses.py ALL
WORKDIR ${PYTHON_DIR}

# Build various files for root (.bash_profile, .sqliterc, entrypoint.sh, etc) and remove unnecessaries
ARG SSH_KEY_DIR
ARG SSH_DIR=/root/.ssh

# Includes an entrypoint.sh that runs 'poetry install' which is needed for pytest to work without
# manually running 'poetry install' (TODO: why?)
ARG ENTRYPOINT_FILE_PATH=${PYTHON_DIR}/entrypoint.sh
RUN echo '.mode table\n.header on' > ${HOME}/.sqliterc && \
    echo 'alias chain_address_db=/ethecycle/scripts/chain_addresses/connect_to_db.sh' >> ${HOME}/.bash_profile && \
    echo '#!/bin/bash\npoetry install\nexec "$@"' > ${ENTRYPOINT_FILE_PATH} && chmod 774 ${ENTRYPOINT_FILE_PATH} && \
    rm -fr ${ETHECYCLE_TMP_DIR_FOR_BUILDING_CHAIN_ADDRESS_DB} && \
    apt-get purge --auto-remove -y wget && \
    mkdir ${SSH_DIR} && chmod 700 ${SSH_DIR}

# Setup ssh (you need to generate the ssh keys before running docker build; see README.md for details)
COPY ${SSH_KEY_DIR}/ ${SSH_DIR}/

# Entrypoints
ENTRYPOINT ["/python/entrypoint.sh"]
CMD ["/bin/bash", "-l"]
