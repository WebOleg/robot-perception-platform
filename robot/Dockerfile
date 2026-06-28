FROM ros:humble-ros-base

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-pip libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir \
        ultralytics==8.3.40 \
        opencv-python-headless==4.10.0.84

# Bake model weights and a sample image into the image (offline, reproducible).
# YOLO() downloads weights into the current working dir, so cd to /assets first.
WORKDIR /assets
RUN python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt'); YOLO('yolov8n-seg.pt')"
# ultralytics' downloader follows redirects (plain urllib does not).
RUN python3 -c "from ultralytics.utils.downloads import safe_download; safe_download('https://ultralytics.com/images/bus.jpg', dir='/assets')" && \
    mv /assets/bus.jpg /assets/sample.jpg

ENV YOLO_MODEL=/assets/yolov8n.pt
ENV SAMPLE_IMAGE=/assets/sample.jpg

WORKDIR /ros2_ws
ARG CACHEBUST=0
COPY ros2_ws/src ./src

RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
