FROM public.ecr.aws/ubuntu/ubuntu@sha256:45e9ddc6895604674618a409ca9f73d301da8fdb75fe330e8e9a27b3b219e4ad
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates libgmp10 libstdc++6 libgomp1 ffmpeg && rm -rf /var/lib/apt/lists/*
ADD bindcraft-env.tar /opt/bindcraft-env/
ADD cuda-cache.tar /opt/bindcraft-env/
COPY BindCraft/ /opt/BindCraft/
COPY params/ /opt/BindCraft/params/
COPY app/ /opt/poreva/
COPY cuda-wheels/ /tmp/cuda-wheels/
RUN /opt/bindcraft-env/bin/python -m pip install --no-cache-dir --no-index --find-links=/tmp/cuda-wheels --no-deps -r /opt/poreva/provenance/requirements-cuda.txt && rm -rf /tmp/cuda-wheels
ENV PATH=/opt/bindcraft-env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LD_LIBRARY_PATH=/opt/bindcraft-env/lib \
    BINDCRAFT_PYTHON=/opt/bindcraft-env/bin/python \
    BINDCRAFT_DIR=/opt/BindCraft \
    MPLBACKEND=Agg \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility
WORKDIR /opt/BindCraft
RUN /bin/bash /opt/poreva/bin/entrypoint.sh cpu-check
ENTRYPOINT ["/bin/bash", "/opt/poreva/bin/entrypoint.sh"]
CMD ["cpu-check"]
