FROM ros:humble-ros-base

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --no-cache-dir aiohttp==3.10.5

WORKDIR /app
COPY frame_service.py .

CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && python3 frame_service.py"]
