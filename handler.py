import runpod
import subprocess
import json
import os
import requests

VOLUME_PATH = "/workspace/volume"
WORKFLOW_INPUT = "workflow-ultrareal.json"
TEMP_WORKFLOW = os.path.join(VOLUME_PATH, "workflow-temp.json")
OUTPUT_IMAGE_PATH = os.path.join(VOLUME_PATH, "output.png")
CHECKPOINT_PATH = os.path.join(VOLUME_PATH, "ultrareal.safetensors")
CHECKPOINT_URL = "https://huggingface.co/Danrisi/UltraReal_finetune_v4/resolve/main/UltraRealistic_FineTune_Project_v3.safetensors"


def download_checkpoint():
    if not os.path.exists(CHECKPOINT_PATH):
        print("📥 Downloading UltraReal checkpoint...")
        os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)
        with requests.get(CHECKPOINT_URL, stream=True) as r:
            r.raise_for_status()
            with open(CHECKPOINT_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("✅ Checkpoint downloaded.")
    else:
        print("✅ Checkpoint already exists.")


def handler(event):
    try:
        print("📦 Starting handler...")

        # Download model if needed
        download_checkpoint()

        # Extract prompt
        prompt = event["input"].get("prompt", "selfie of a girl, visible JPEG artifacts")
        print("📌 Using prompt:", prompt)

        # Load workflow
        with open(WORKFLOW_INPUT, "r") as f:
            workflow = json.load(f)
        print("🧠 Workflow loaded.")

        # Inject prompt
        workflow["2"]["inputs"]["text"] = prompt

        # Save modified workflow
        with open(TEMP_WORKFLOW, "w") as f:
            json.dump(workflow, f)
        print("📝 Updated workflow saved to temp file.")

        # Run ComfyUI headless
        print("⚙️ Launching ComfyUI process...")
        subprocess.run([
            "python3", "ComfyUI/main.py",
            "--workflow", TEMP_WORKFLOW
        ], check=True)
        print("✅ ComfyUI process completed.")

        # Return output path
        return {"output": OUTPUT_IMAGE_PATH}

    except subprocess.CalledProcessError as e:
        print("❌ ComfyUI subprocess failed:", str(e))
        return {"error": "ComfyUI process failed", "details": str(e)}

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        return {"error": "Unexpected server error", "details": str(e)}


runpod.serverless.start({"handler": handler})
