import runpod
import subprocess
import json
import os
import requests
import shutil
import uuid
import traceback

BASE_VOLUME_PATH = "/workspace/volume"
CHECKPOINT_FILENAME = "ultrarealFineTune_v4.safetensors"
CHECKPOINT_URL = "https://huggingface.co/Danrisi/UltraReal_finetune_v4/resolve/main/UltraRealistic_FineTune_Project_v3.safetensors"
CHECKPOINT_PATH = os.path.join(BASE_VOLUME_PATH, CHECKPOINT_FILENAME)
WORKFLOW_INPUT = os.path.join(BASE_VOLUME_PATH, "workflow-ultrareal.json")


def download_checkpoint():
    if not os.path.exists(CHECKPOINT_PATH):
        print("📥 Downloading UltraReal checkpoint...")
        os.makedirs(BASE_VOLUME_PATH, exist_ok=True)
        with requests.get(CHECKPOINT_URL, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(CHECKPOINT_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("✅ Checkpoint downloaded.")
    else:
        print("✅ Checkpoint already exists.")


def handler(event):
    job_id = event.get("id", str(uuid.uuid4()))
    print(f"🚀 Starting job: {job_id}")

    job_dir = os.path.join(BASE_VOLUME_PATH, f"job-{job_id}")
    os.makedirs(job_dir, exist_ok=True)

    TEMP_WORKFLOW = os.path.join(job_dir, "workflow-temp.json")
    OUTPUT_IMAGE_PATH = os.path.join(job_dir, "output.png")

    try:
        download_checkpoint()

        prompt = event["input"].get("prompt", "selfie of a girl, visible JPEG artifacts")
        print("📌 Prompt:", prompt)

        with open(WORKFLOW_INPUT, "r") as f:
            workflow = json.load(f)

        workflow["2"]["inputs"]["text"] = prompt
        workflow["11"]["inputs"]["output_path"] = OUTPUT_IMAGE_PATH

        with open(TEMP_WORKFLOW, "w") as f:
            json.dump(workflow, f)

        print("🧠 Workflow patched + saved.")

        print("⚙️ Running ComfyUI...")
        subprocess.run([
            "python3", "ComfyUI/main.py",
            "--workflow", TEMP_WORKFLOW
        ], check=True)

        if not os.path.exists(OUTPUT_IMAGE_PATH):
            raise FileNotFoundError("Output image not found after generation.")

        size_mb = os.path.getsize(OUTPUT_IMAGE_PATH) / 1024 / 1024
        print(f"✅ Output generated ({size_mb:.2f} MB) at {OUTPUT_IMAGE_PATH}")

        return {
            "status": "success",
            "output": OUTPUT_IMAGE_PATH,
            "size_mb": round(size_mb, 2)
        }

    except subprocess.CalledProcessError as e:
        print("❌ ComfyUI failed:", str(e))
        return {"status": "failed", "error": "ComfyUI process failed", "details": str(e)}

    except Exception as e:
        print("❌ Exception:", str(e))
        return {"status": "failed", "error": "Unexpected server error", "details": str(e), "trace": traceback.format_exc()}

    finally:
        if os.path.exists(job_dir):
            shutil.rmtree(job_dir, ignore_errors=True)
            print(f"🧹 Cleaned job directory: {job_dir}")


# 🔥 Required to run on RunPod!
runpod.serverless.start({"handler": handler})
