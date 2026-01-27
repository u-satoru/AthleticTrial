# クライミングシステム - 入力設計ドキュメント

## 概要

このドキュメントは、AthleticTrial プロジェクトにおけるクライミングシステムの入力設計を定義します。

## Input Mapping Context の役割

| IMC | 用途 | 有効タイミング | Priority |
|-----|------|---------------|----------|
| **IMC_Sandbox** | 通常操作（移動、カメラ、ジャンプ、Fキー壁吸着） | 常時有効 | 0 |
| **IMC_Climbing** | 壁移動（WASD）、Gキー離脱 | 壁吸着中のみ有効 | 1 |

## キーマッピング

### IMC_Sandbox

| Input Action | キー | 説明 |
|-------------|------|------|
| IA_Move | WASD | 通常移動 |
| IA_Look | マウス | カメラ操作 |
| IA_Jump | Space | ジャンプ |
| IA_GrabWall | F | 壁吸着開始 |
| その他 | ... | 通常ゲーム操作 |

### IMC_Climbing

| Input Action | キー | 説明 |
|-------------|------|------|
| IA_ClimbMove / IA_ClimbUp/Down/Left/Right | WASD | 壁移動 |
| IA_Release | G | 壁離脱 |
| IA_Look | マウス | カメラ操作（オプション） |

## 状態遷移フロー

```
[通常状態]
  │ IMC_Sandbox (Priority: 0) 有効
  │ Movement Mode: Walking
  │
  ├─ Fキー押下 → TryGrabWall
  │
  ▼
[壁吸着]
  │ ┌─────────────────────────────────────┐
  │ │ 1. Set Movement Mode (Flying)       │
  │ │ 2. Add Mapping Context              │
  │ │    (IMC_Climbing, Priority: 1)      │
  │ │ 3. EnableWallClimbingTick           │
  │ │ 4. CallOnClimbingStarted            │
  │ └─────────────────────────────────────┘
  │
  │ IMC_Sandbox (Priority: 0) 有効
  │ IMC_Climbing (Priority: 1) 有効 ← 追加
  │ Movement Mode: Flying
  │
  ├─ WASDキー → 壁移動（IMC_Climbing で処理）
  ├─ Gキー押下 → ReleaseFromWall
  │
  ▼
[壁離脱]
  │ ┌─────────────────────────────────────┐
  │ │ 1. Remove Mapping Context           │
  │ │    (IMC_Climbing)                   │
  │ │ 2. Set Movement Mode (Walking)      │
  │ │ 3. DisableAllClimbingTicks          │
  │ │ 4. CallOnClimbingStopped            │
  │ └─────────────────────────────────────┘
  │
  ▼
[通常状態に戻る]
```

## Blueprint 実装詳細

### TryGrabWall 関数（AC_Climbing）

```
TryGrabWall
  │
  ├─ CheckForClimbableSurface
  │     └─ Line Trace (Control Rotation Forward)
  │
  ├─ [条件チェック]
  │     └─ !bIsClimbing AND !IsFalling AND bHitWall
  │
  ├─ AttachToWall (HitResult)
  │     ├─ SetWallNormal
  │     ├─ SetTargetWallRotation
  │     └─ SetWallHitLocation (ImpactPoint + WallNormal * WallOffset)
  │
  ├─ Set Movement Mode (Flying)
  │
  ├─ Add Mapping Context (IMC_Climbing, Priority: 1)
  │     ├─ GetOwnerCharacter
  │     ├─ GetController
  │     ├─ Cast to PlayerController
  │     ├─ GetEnhancedInputLocalPlayerSubsystem
  │     └─ AddMappingContext (IMC_Climbing, Priority: 1)
  │
  ├─ CallOnClimbingStarted
  │
  └─ EnableWallClimbingTick
```

### ReleaseFromWall 関数（AC_Climbing）

```
ReleaseFromWall
  │
  ├─ Remove Mapping Context (IMC_Climbing)
  │     ├─ GetOwnerCharacter
  │     ├─ GetController
  │     ├─ Cast to PlayerController
  │     ├─ GetEnhancedInputLocalPlayerSubsystem
  │     └─ RemoveMappingContext (IMC_Climbing)
  │
  ├─ Set Movement Mode (Walking)
  │     ├─ GetOwnerCharacter
  │     ├─ GetCharacterMovement
  │     └─ SetMovementMode (Walking)
  │
  ├─ DisableAllClimbingTicks
  │
  └─ CallOnClimbingStopped
```

### CBP_SandboxCharacter イベントハンドラー

```
[IA_GrabWall - Started]
  │
  ├─ PrintString "GrabWall Triggered"
  ├─ GetClimbingComponent
  └─ ToggleAttach
        └─ if !bIsClimbing → TryGrabWall

[IA_Release - Started]  ※ IMC_Climbing から受信
  │
  ├─ PrintString "ReleaseWall Triggered"
  ├─ GetClimbingComponent
  └─ ReleaseFromWall
```

## 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-01-27 | 初版作成 - 入力設計の基本構造を定義 |

## 注意事項

1. **BeginPlay での IMC_Climbing 追加は不要**
   - 壁吸着時に動的に追加・削除する

2. **Priority の重要性**
   - IMC_Climbing (Priority: 1) > IMC_Sandbox (Priority: 0)
   - 壁吸着中は IMC_Climbing の入力が優先される

3. **Movement Mode の管理**
   - Flying: 壁吸着中（重力無効）
   - Walking: 通常状態

4. **GASP との連携**
   - OnClimbingStarted → StartClimbing_GASP
   - OnClimbingStopped → StopClimbing_GASP
