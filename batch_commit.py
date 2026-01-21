#!/usr/bin/env python3
"""
Git Batch Commit Script
プロジェクトを1コミットあたり指定サイズ以内に分けてコミットする
"""

import subprocess
import sys
import time
from pathlib import Path

# 設定
MAX_COMMIT_SIZE_MB = 200
MAX_COMMIT_SIZE_BYTES = MAX_COMMIT_SIZE_MB * 1024 * 1024
REPO_PATH = Path(r"c:\Users\work0\uechi\UEProjects\AthleticTrial")


def remove_lock_file():
    """Git lock ファイルを削除"""
    lock_file = REPO_PATH / ".git" / "index.lock"
    if lock_file.exists():
        try:
            lock_file.unlink()
            print("  Removed stale lock file")
            time.sleep(0.5)
        except Exception as e:
            print(f"  Warning: Could not remove lock file: {e}")


def run_git(args: list[str], capture_output: bool = True, retries: int = 3) -> subprocess.CompletedProcess:
    """Gitコマンドを実行（リトライ機能付き）"""
    for attempt in range(retries):
        result = subprocess.run(
            ["git"] + args,
            cwd=REPO_PATH,
            capture_output=capture_output,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if result.returncode == 0:
            return result
        if "index.lock" in result.stderr:
            remove_lock_file()
            time.sleep(1)
            continue
        break
    return result


def get_staged_files() -> list[tuple[str, int]]:
    """ステージングされたファイルとそのサイズを取得"""
    files_with_size = []

    result = run_git(["diff", "--cached", "--name-only"])
    if result.returncode == 0:
        for file in result.stdout.strip().split("\n"):
            if file:
                file_path = REPO_PATH / file
                if file_path.exists() and file_path.is_file():
                    size = file_path.stat().st_size
                    files_with_size.append((file, size))

    return files_with_size


def get_untracked_and_modified_files() -> list[tuple[str, int]]:
    """未追跡・変更ファイルとそのサイズを取得"""
    files_with_size = []

    # 未追跡ファイルを取得
    result = run_git(["ls-files", "--others", "--exclude-standard"])
    if result.returncode == 0:
        for file in result.stdout.strip().split("\n"):
            if file:
                file_path = REPO_PATH / file
                if file_path.exists() and file_path.is_file():
                    size = file_path.stat().st_size
                    files_with_size.append((file, size))

    # 変更されたファイル（未ステージング）を取得
    result = run_git(["diff", "--name-only"])
    if result.returncode == 0:
        for file in result.stdout.strip().split("\n"):
            if file:
                file_path = REPO_PATH / file
                if file_path.exists() and file_path.is_file():
                    size = file_path.stat().st_size
                    # 重複を避ける
                    if not any(f[0] == file for f in files_with_size):
                        files_with_size.append((file, size))

    return files_with_size


def get_all_pending_files() -> list[tuple[str, int]]:
    """ステージング済み + 未ステージングの全ファイルを取得"""
    files_with_size = []
    seen_files = set()

    # ステージングされたファイル
    staged = get_staged_files()
    for file, size in staged:
        if file not in seen_files:
            files_with_size.append((file, size))
            seen_files.add(file)

    # 未追跡・変更ファイル
    untracked = get_untracked_and_modified_files()
    for file, size in untracked:
        if file not in seen_files:
            files_with_size.append((file, size))
            seen_files.add(file)

    return files_with_size


def create_batches(files: list[tuple[str, int]]) -> list[list[tuple[str, int]]]:
    """ファイルをバッチに分割（各バッチはMAX_COMMIT_SIZE_BYTES以内）"""
    batches = []
    current_batch = []
    current_size = 0

    # サイズの大きい順にソート（大きいファイルを先に処理）
    sorted_files = sorted(files, key=lambda x: x[1], reverse=True)

    for file, size in sorted_files:
        # 単一ファイルが上限を超える場合は単独でバッチに
        if size > MAX_COMMIT_SIZE_BYTES:
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_size = 0
            batches.append([(file, size)])
            print(f"  Warning: {file} ({size / 1024 / 1024:.2f} MB) exceeds limit, will be committed alone")
            continue

        # 現在のバッチに追加できるか確認
        if current_size + size <= MAX_COMMIT_SIZE_BYTES:
            current_batch.append((file, size))
            current_size += size
        else:
            # 新しいバッチを開始
            if current_batch:
                batches.append(current_batch)
            current_batch = [(file, size)]
            current_size = size

    # 最後のバッチを追加
    if current_batch:
        batches.append(current_batch)

    return batches


def reset_staging() -> bool:
    """ステージングをリセット"""
    result = run_git(["reset", "HEAD"])
    return result.returncode == 0


def commit_batch(batch: list[tuple[str, int]], batch_num: int, total_batches: int) -> bool:
    """バッチをコミット"""
    files = [f[0] for f in batch]
    total_size_mb = sum(f[1] for f in batch) / 1024 / 1024

    print(f"\n--- Batch {batch_num}/{total_batches} ({total_size_mb:.2f} MB, {len(files)} files) ---")

    # ファイルをステージング
    for file in files:
        result = run_git(["add", file])
        if result.returncode != 0:
            print(f"  Error: Failed to stage {file}")
            print(f"  {result.stderr}")
            return False

    # コミット
    commit_msg = f"Batch commit {batch_num}/{total_batches} ({len(files)} files, {total_size_mb:.2f} MB)"
    result = run_git(["commit", "-m", commit_msg])

    if result.returncode != 0:
        print(f"  Error: Commit failed")
        print(f"  {result.stderr}")
        return False

    print(f"  Committed: {commit_msg}")
    return True


def main():
    # コマンドライン引数で自動実行モードを確認
    auto_mode = "--yes" in sys.argv or "-y" in sys.argv

    print("=" * 60)
    print("Git Batch Commit Script")
    print(f"Max commit size: {MAX_COMMIT_SIZE_MB} MB")
    print(f"Repository: {REPO_PATH}")
    print("=" * 60)

    # Gitリポジトリか確認
    result = run_git(["rev-parse", "--git-dir"])
    if result.returncode != 0:
        print("Error: Not a git repository")
        return

    # 全ファイルを取得
    print("\nCollecting files...")
    files = get_all_pending_files()

    if not files:
        print("No files to commit")
        return

    total_size_mb = sum(f[1] for f in files) / 1024 / 1024
    print(f"Total files: {len(files)}")
    print(f"Total size: {total_size_mb:.2f} MB")

    # 一度全てのステージングをリセット
    print("\nResetting staging area...")
    run_git(["reset"])

    # バッチに分割
    print("\nCreating batches...")
    batches = create_batches(files)
    print(f"Number of batches: {len(batches)}")

    # 各バッチの概要を表示
    print("\n--- Batch Summary ---")
    for i, batch in enumerate(batches, 1):
        batch_size_mb = sum(f[1] for f in batch) / 1024 / 1024
        print(f"  Batch {i}: {len(batch)} files, {batch_size_mb:.2f} MB")

    # 確認
    if not auto_mode:
        print("\n" + "=" * 60)
        try:
            response = input("Execute commits? (y/N): ").strip().lower()
            if response != "y":
                print("Cancelled")
                return
        except EOFError:
            print("\nNo input available. Use --yes or -y flag for auto mode.")
            print("Example: python batch_commit.py --yes")
            return
    else:
        print("\nAuto mode enabled, proceeding with commits...")

    # コミット実行
    print("\nExecuting commits...")
    success_count = 0
    for i, batch in enumerate(batches, 1):
        if commit_batch(batch, i, len(batches)):
            success_count += 1
        else:
            print(f"\nError occurred at batch {i}. Stopping.")
            break

    print("\n" + "=" * 60)
    print(f"Done: {success_count}/{len(batches)} batches committed")


if __name__ == "__main__":
    main()
