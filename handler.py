import runpod
import subprocess
import json
import os
import requests

WORKFLOW_INPUT = "workflow-ultrareal.json"
TEMP_WORKFLOW = "workflow-temp.json"
OUTPUT_IMAGE_PATH = "/workspace/ComfyUI/output/ComfyUI_00001_.png"

def download_checkpoint():
    path = "ComfyUI/models/checkpoints/ultrarealFineTune_v4.safetensors"
    url = "https://huggingface.co/Danrisi/UltraReal_finetune_v4/resolve/main/UltraRealistic_FineTune_Project_v3.safetensors"

    if not os.path.exists(path):
        print("Downloading UltraReal checkpoint...")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
def handler(event):
    
    download_checkpoint()  # <-- required
    # Extract prompt from input
    prompt = event["input"].get("prompt", "selfie of a girl, visible JPEG artifacts")

    # Load original workflow
    with open(WORKFLOW_INPUT, "r") as f:
        workflow = json.load(f)

    # Replace prompt in node 2
    workflow["2"]["inputs"]["text"] = prompt

    # Save temp workflow file
    with open(TEMP_WORKFLOW, "w") as f:
        json.dump(workflow, f)

    # Run ComfyUI with headless call
    subprocess.run([
        "python3", "ComfyUI/main.py",
        "--workflow", TEMP_WORKFLOW
    ], check=True)

    # Return image path (RunPod auto-exposes /workspace for downloads)
    return {"output": OUTPUT_IMAGE_PATH}

runpod.serverless.start({"handler": handler})
