"""Build and deploy Lambda functions to AWS. Run from repo root."""
import subprocess, sys, os, shutil, zipfile, boto3
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SERVICES_DIR = REPO_ROOT / "services"
REGION = "us-east-1"
ENV = "prod"

SERVICES = {
    "api": [
        "handler.py", "db.py", "models.py", "router.py", "routes"
    ],
    "events-scraper": [
        "handler.py", "config", "scrapers"
    ],
    "image-gen": [
        "handler.py", "alt_text.py", "enhancer.py", "generator.py",
        "processor.py", "prompts.py", "sourcer.py", "uploader.py"
    ],
    "content-generator": [
        "handler.py", "post_builder.py", "prompts.py", "github_trigger.py", "ssm.py"
    ],
}

def add_to_zip(zf, path, arcname=None):
    """Recursively add file or directory to zip."""
    path = Path(path)
    if not path.exists():
        return
    if path.is_file():
        zf.write(path, arcname or path.name)
    elif path.is_dir():
        base = arcname or path.name
        for child in path.rglob("*"):
            if child.is_file() and "__pycache__" not in child.parts and child.suffix != ".pyc":
                zf.write(child, str(Path(base) / child.relative_to(path)))

def deploy(svc, src_files):
    function_name = f"novakidlife-{ENV}-{svc}"
    svc_dir = SERVICES_DIR / svc
    pkg_dir = svc_dir / "package"
    zip_path = svc_dir / "deploy.zip"

    print(f"\n==> Deploying {svc}...")

    # Clean up
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    if zip_path.exists():
        zip_path.unlink()
    pkg_dir.mkdir()

    # Install dependencies for Linux Lambda
    print("    Installing dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install",
        "-r", str(svc_dir / "requirements.txt"),
        "--target", str(pkg_dir),
        "--platform", "manylinux2014_x86_64",
        "--implementation", "cp",
        "--python-version", "3.12",
        "--only-binary=:all:",
        "--upgrade",
        "--quiet"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"    ERROR: {result.stderr}")
        sys.exit(1)

    # Build zip
    print("    Zipping...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add dependencies
        for item in pkg_dir.iterdir():
            add_to_zip(zf, item)
        # Add source files
        for f in src_files:
            add_to_zip(zf, svc_dir / f)

    size_kb = zip_path.stat().st_size // 1024
    print(f"    Package size: {size_kb} KB")

    # Upload to Lambda (via S3 if > 50 MB)
    print(f"    Uploading to {function_name}...")
    session = boto3.session.Session(profile_name="default")
    client = session.client("lambda", region_name=REGION)
    size_bytes = zip_path.stat().st_size

    if size_bytes > 50 * 1024 * 1024:
        print("    Large package — uploading via S3...")
        s3 = session.client("s3", region_name=REGION)
        s3_key = f"lambda-deploys/{svc}/deploy.zip"
        s3.upload_file(str(zip_path), "novakidlife-tfstate", s3_key)
        response = client.update_function_code(
            FunctionName=function_name,
            S3Bucket="novakidlife-tfstate",
            S3Key=s3_key
        )
    else:
        with open(zip_path, "rb") as f:
            response = client.update_function_code(
                FunctionName=function_name,
                ZipFile=f.read()
            )
    print(f"    Uploaded: {response['CodeSize']} bytes")

    # Wait for update to complete
    print("    Waiting for update...")
    waiter = client.get_waiter("function_updated")
    waiter.wait(FunctionName=function_name)

    # Clean up
    shutil.rmtree(pkg_dir)
    zip_path.unlink()
    print(f"    Done: {svc}")

if __name__ == "__main__":
    targets = sys.argv[1:] or list(SERVICES.keys())
    for svc in targets:
        deploy(svc, SERVICES[svc])
    print("\nAll Lambda functions deployed successfully.")
