import runpod
import subprocess
import json
import os

WORKFLOW_INPUT = "workflow-ultrareal.json"
TEMP_WORKFLOW = "workflow-temp.json"
OUTPUT_IMAGE_PATH = "/workspace/ComfyUI/output/ComfyUI_00001_.png"

def handler(event):
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
