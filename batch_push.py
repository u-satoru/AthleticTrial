#!/usr/bin/env python3
"""
Git Batch Push Script
1コミットずつリモートにプッシュする
"""

import subprocess
import sys
import time
from pathlib import Path

# 設定
REPO_PATH = Path(r"d:\UnrealProjects\AthleticTrial")
REMOTE_NAME = "origin"
BRANCH_NAME = "main"


def run_git(args: list[str], capture_output: bool = True, timeout: int = 600) -> subprocess.CompletedProcess:
    """Gitコマンドを実行"""
    result = subprocess.run(
        ["git"] + args,
        cwd=REPO_PATH,
        capture_output=capture_output,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout
    )
    return result


def get_all_commits() -> list[tuple[str, str]]:
    """全コミットを古い順に取得 (hash, message)"""
    result = run_git(["log", "--reverse", "--format=%H|%s"])
    if result.returncode != 0:
        return []

    commits = []
    for line in result.stdout.strip().split("\n"):
        if line and "|" in line:
            hash_val, message = line.split("|", 1)
            commits.append((hash_val.strip(), message.strip()))
    return commits


def get_pushed_commits() -> set[str]:
    """リモートにプッシュ済みのコミットハッシュを取得"""
    # リモートの最新情報を取得
    run_git(["fetch", REMOTE_NAME])

    # リモートブランチが存在するか確認
    result = run_git(["rev-parse", "--verify", f"{REMOTE_NAME}/{BRANCH_NAME}"])
    if result.returncode != 0:
        return set()  # リモートブランチがない場合は空

    # リモートにあるコミットを取得
    result = run_git(["log", f"{REMOTE_NAME}/{BRANCH_NAME}", "--format=%H"])
    if result.returncode != 0:
        return set()

    return set(line.strip() for line in result.stdout.strip().split("\n") if line.strip())


def push_single_commit(commit_hash: str, commit_num: int, total: int) -> bool:
    """単一コミットをプッシュ"""
    print(f"\n--- Push {commit_num}/{total} ---")
    print(f"  Commit: {commit_hash[:8]}")

    # そのコミットまでの履歴をプッシュ
    result = run_git(
        ["push", REMOTE_NAME, f"{commit_hash}:refs/heads/{BRANCH_NAME}"],
        timeout=600
    )

    if result.returncode != 0:
        print(f"  Error: Push failed")
        print(f"  {result.stderr}")
        return False

    print(f"  Success!")
    return True


def main():
    auto_mode = "--yes" in sys.argv or "-y" in sys.argv

    print("=" * 60)
    print("Git Batch Push Script")
    print(f"Repository: {REPO_PATH}")
    print(f"Remote: {REMOTE_NAME}")
    print(f"Branch: {BRANCH_NAME}")
    print("=" * 60)

    # Gitリポジトリか確認
    result = run_git(["rev-parse", "--git-dir"])
    if result.returncode != 0:
        print("Error: Not a git repository")
        return

    # 全コミットを取得
    print("\nCollecting commits...")
    all_commits = get_all_commits()

    if not all_commits:
        print("No commits found")
        return

    print(f"Total commits: {len(all_commits)}")

    # プッシュ済みコミットを確認
    print("\nChecking remote...")
    pushed_commits = get_pushed_commits()
    print(f"Already pushed: {len(pushed_commits)} commits")

    # 未プッシュコミットを抽出
    unpushed_commits = [(h, m) for h, m in all_commits if h not in pushed_commits]

    if not unpushed_commits:
        print("\nAll commits are already pushed!")
        return

    print(f"Commits to push: {len(unpushed_commits)}")

    # 未プッシュコミットの概要を表示
    print("\n--- Commits to Push ---")
    for i, (hash_val, message) in enumerate(unpushed_commits, 1):
        print(f"  {i}. {hash_val[:8]} - {message[:50]}{'...' if len(message) > 50 else ''}")

    # 確認
    if not auto_mode:
        print("\n" + "=" * 60)
        try:
            response = input("Execute push? (y/N): ").strip().lower()
            if response != "y":
                print("Cancelled")
                return
        except EOFError:
            print("\nNo input available. Use --yes or -y flag for auto mode.")
            print("Example: python batch_push.py --yes")
            return
    else:
        print("\nAuto mode enabled, proceeding with push...")

    # プッシュ実行
    print("\nExecuting push...")
    success_count = 0

    for i, (hash_val, message) in enumerate(unpushed_commits, 1):
        print(f"\n  [{i}/{len(unpushed_commits)}] {message[:40]}...")
        if push_single_commit(hash_val, i, len(unpushed_commits)):
            success_count += 1
            # プッシュ間に少し待機（レート制限対策）
            if i < len(unpushed_commits):
                time.sleep(1)
        else:
            print(f"\nError occurred at commit {i}. Stopping.")
            break

    print("\n" + "=" * 60)
    print(f"Done: {success_count}/{len(unpushed_commits)} commits pushed")


if __name__ == "__main__":
    main()
