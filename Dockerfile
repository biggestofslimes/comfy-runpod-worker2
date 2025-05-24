FROM nvidia/cuda:12.2.0-base-ubuntu22.04

# Install basic packages
RUN apt update && apt install -y python3 python3-pip git wget

# Set Python alias
RUN ln -s /usr/bin/python3 /usr/bin/python

# Clone ComfyUI
WORKDIR /workspace
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /workspace/ComfyUI

# Install Python dependencies
RUN pip install -r requirements.txt
RUN pip install runpod requests

# Download UltraReal checkpoint
RUN mkdir -p /workspace/ComfyUI/models/checkpoints

# Copy handler and workflow
COPY handler.py /workspace/
COPY workflow-ultrareal.json /workspace/

# Set working dir and start handler
WORKDIR /workspace
CMD ["python3", "handler.py"]
