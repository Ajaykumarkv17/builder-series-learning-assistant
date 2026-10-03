"""Preflight doctor for the Learning Assistant series.

Verifies, in order:
  1. AWS credentials resolve (STS GetCallerIdentity).
  2. The configured region is set.
  3. The Amazon Nova models this series uses are listed in Bedrock for this account/region.
  4. A live Converse smoke test against Nova Lite actually returns a completion.

Run:  python -m learning_assistant.doctor
Exit code 0 = all good; non-zero = something to fix (message says what).

Requires AWS credentials configured in your terminal first, e.g.:
    aws configure            # or: aws sso login --profile <name>
    export AWS_PROFILE=<name>
    export AWS_REGION=us-east-1
"""
from __future__ import annotations

import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from .config import ALL_MODEL_IDS, AWS_REGION, NOVA_LITE, Task, model_id_for

OK = "[ OK ]"
FAIL = "[FAIL]"
WARN = "[WARN]"


def _check_credentials() -> bool:
    try:
        ident = boto3.client("sts", region_name=AWS_REGION).get_caller_identity()
    except (NoCredentialsError, ClientError, BotoCoreError) as e:
        print(f"{FAIL} AWS credentials: {e}")
        print("       Fix: run `aws configure` or `aws sso login`, then set AWS_PROFILE.")
        return False
    print(f"{OK} AWS credentials — account {ident['Account']}, arn {ident['Arn']}")
    return True


def _check_region() -> bool:
    if not AWS_REGION:
        print(f"{FAIL} Region not set. Export AWS_REGION=us-east-1.")
        return False
    print(f"{OK} Region — {AWS_REGION}")
    return True


def _check_model_access() -> bool:
    """Confirm the Nova models are present in this account/region."""
    try:
        bedrock = boto3.client("bedrock", region_name=AWS_REGION)
        resp = bedrock.list_foundation_models(byProvider="Amazon")
    except (ClientError, BotoCoreError) as e:
        print(f"{FAIL} Could not list foundation models: {e}")
        return False

    available = {m["modelId"] for m in resp.get("modelSummaries", [])}
    all_ok = True
    for mid in ALL_MODEL_IDS:
        if any(mid in a for a in available):
            print(f"{OK} Model listed — {mid}")
        else:
            print(f"{WARN} Model NOT listed — {mid}")
            print("       Enable it in Bedrock console → Model access, in this region.")
            all_ok = False
    return all_ok


def _check_converse_smoke() -> bool:
    """Live Converse call against Nova Lite — proves end-to-end invoke works."""
    model_id = model_id_for(Task.FAST)  # Nova Lite inference profile
    try:
        rt = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        resp = rt.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Reply with the single word: ready"}]}],
            inferenceConfig={"maxTokens": 16, "temperature": 0.0},
        )
    except (ClientError, BotoCoreError) as e:
        print(f"{FAIL} Converse smoke test ({NOVA_LITE.name} via {model_id}): {e}")
        print("       Common fixes: enable model access; use the us. inference profile; check IAM.")
        return False
    text = "".join(
        b.get("text", "") for b in resp["output"]["message"]["content"]
    ).strip()
    print(f"{OK} Converse smoke test — {NOVA_LITE.name} replied: {text!r}")
    return True


def main() -> int:
    print("Learning Assistant — preflight doctor\n" + "-" * 38)
    checks = [
        _check_credentials,
        _check_region,
        _check_model_access,
        _check_converse_smoke,
    ]
    results = [c() for c in checks]
    print("-" * 38)
    if all(results):
        print("All checks passed. You're ready for Article 2.")
        return 0
    print("Some checks failed — see messages above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
