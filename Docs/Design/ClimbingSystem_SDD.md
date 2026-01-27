# クライミングシステム - SDD（Spec Driven Development）仕様書

## 1. 概要

### 1.1 目的
AnimationTestProject から AthleticTrial へクライミングシステムを移行し、GASP（Game Animation Sample Plugin）と統合する。

### 1.2 スコープ
- 壁吸着（Wall Attach）
- 壁移動（Wall Climb）
- 壁離脱（Wall Release）
- 頂上登り（Ledge Climb）

### 1.3 関連ドキュメント
- [ClimbingSystem_InputDesign.md](ClimbingSystem_InputDesign.md) - 入力設計詳細

---

## 2. 機能要件

### 2.1 壁吸着（Wall Attach）

| 項目 | 仕様 |
|------|------|
| トリガー | F キー押下 |
| 前提条件 | !bIsClimbing AND !IsFalling AND 壁検出成功 |
| 壁検出方法 | Control Rotation Forward 方向に Line Trace |
| 結果 | キャラクターが壁に吸着、Movement Mode = Flying |

### 2.2 壁移動（Wall Climb）

| 項目 | 仕様 |
|------|------|
| トリガー | WASD キー（壁吸着中） |
| 動作 | 壁表面に沿って上下左右に移動 |
| 制約 | 壁の範囲内でのみ移動可能 |

### 2.3 壁離脱（Wall Release）

| 項目 | 仕様 |
|------|------|
| トリガー | G キー押下（頂上未到達時） |
| 結果 | キャラクターが壁から離脱、Movement Mode = Walking |

### 2.4 頂上登り（Ledge Climb）

| 項目 | 仕様 |
|------|------|
| トリガー | G キー押下（頂上到達時） |
| 頂上検出方法 | 頭上オフセット位置から Line Trace、壁を見失ったら頂上 |
| 結果 | キャラクターが壁の上に登って立つ |

---

## 3. 入力仕様

### 3.1 Input Mapping Context

| IMC | 用途 | 有効タイミング | Priority |
|-----|------|---------------|----------|
| IMC_Sandbox | 通常操作 + 壁吸着開始 | 常時有効 | 0 |
| IMC_Climbing | 壁移動 + 離脱/頂上登り | 壁吸着中のみ | 1 |

### 3.2 キーマッピング

#### IMC_Sandbox
| Input Action | キー | 説明 |
|-------------|------|------|
| IA_Move | WASD | 通常移動 |
| IA_Look | マウス | カメラ操作 |
| IA_Jump | Space | ジャンプ |
| IA_GrabWall | F | 壁吸着開始 |

#### IMC_Climbing
| Input Action | キー | 説明 |
|-------------|------|------|
| IA_ClimbMove | WASD | 壁移動 |
| IA_Release | G | 壁離脱 / 頂上登り（コンテキスト依存） |
| IA_Look | マウス | カメラ操作 |

### 3.3 G キーのコンテキスト依存動作

```
G キー押下時:
  if bIsAtLedge == true:
    → LedgeClimb()    // 頂上に登る
  else:
    → ReleaseFromWall() // 壁離脱
```

---

## 4. 状態遷移

### 4.1 状態定義

| 状態 | 説明 | Movement Mode |
|------|------|---------------|
| Normal | 通常状態 | Walking |
| WallClimbing | 壁吸着中 | Flying |
| LedgeReached | 頂上到達（壁吸着中） | Flying |
| LedgeClimbing | 頂上登り中（アニメーション再生中） | Flying |

### 4.2 状態遷移図

```
                    ┌──────────────────────────────────────────┐
                    │                                          │
                    ▼                                          │
┌─────────┐    F キー    ┌──────────────┐                      │
│ Normal  │─────────────▶│ WallClimbing │                      │
└─────────┘              └──────────────┘                      │
     ▲                         │  │                            │
     │                         │  │                            │
     │         G キー          │  │  壁上端検出                │
     │    (頂上未到達時)       │  │                            │
     │◀────────────────────────┘  │                            │
     │                            ▼                            │
     │                   ┌──────────────┐                      │
     │                   │ LedgeReached │                      │
     │                   └──────────────┘                      │
     │                            │                            │
     │                            │ G キー                     │
     │                            │ (頂上到達時)               │
     │                            ▼                            │
     │                   ┌───────────────┐                     │
     │                   │ LedgeClimbing │                     │
     │                   └───────────────┘                     │
     │                            │                            │
     │                            │ アニメーション完了         │
     └────────────────────────────┴────────────────────────────┘
```

---

## 5. コンポーネント設計

### 5.1 AC_Climbing（Actor Component）

#### 変数

| 変数名 | 型 | 説明 |
|--------|-----|------|
| bIsClimbing | bool | クライミング中フラグ |
| bIsWallClimbingActive | bool | 壁クライミング Tick 有効フラグ |
| bIsLedgeClimbingActive | bool | Ledge クライミング Tick 有効フラグ |
| bIsAtLedge | bool | 頂上到達フラグ |
| WallNormal | Vector | 壁の法線ベクトル |
| WallHitLocation | Vector | 壁のヒット位置（オフセット込み） |
| TargetWallRotation | Rotator | 壁に向かう目標回転 |
| WallOffset | float | 壁からのオフセット距離（デフォルト: 60.0） |
| TraceLength | float | Line Trace の長さ |
| LedgeTraceOffset | Vector | 頂上検出用 Trace のオフセット |
| LocationInterpSpeed | float | 位置補間速度（デフォルト: 100.0） |
| RotationInterpSpeed | float | 回転補間速度（デフォルト: 100.0） |

#### 関数

| 関数名 | 説明 |
|--------|------|
| TryGrabWall | 壁吸着を試行 |
| ReleaseFromWall | 壁から離脱 |
| LedgeClimb | 頂上に登る |
| CheckForClimbableSurface | 壁検出 Line Trace |
| CheckForLedge | 頂上検出 Line Trace |
| AttachToWall | 壁に吸着処理 |
| UpdateWallAttachment | 壁吸着位置の更新（Tick） |
| EnableWallClimbingTick | 壁クライミング Tick 有効化 |
| DisableAllClimbingTicks | 全クライミング Tick 無効化 |
| HandleClimbInput | 壁移動入力処理 |

#### Event Dispatcher

| イベント名 | 発火タイミング |
|------------|----------------|
| OnClimbingStarted | 壁吸着開始時 |
| OnClimbingStopped | 壁離脱/頂上登り完了時 |
| OnLedgeReached | 頂上到達時 |

### 5.2 CBP_SandboxCharacter

#### イベントハンドラー

| イベント | 処理 |
|----------|------|
| IA_GrabWall (Started) | ToggleAttach → TryGrabWall |
| IA_Release (Started) | HandleReleaseInput（コンテキスト依存処理） |
| IA_ClimbMove | HandleClimbInput |

---

## 6. 実装詳細

### 6.1 壁検出（CheckForClimbableSurface）

```
Start: GetActorLocation()
Direction: GetControlRotation() → GetForwardVector()
End: Start + Direction * TraceLength

Line Trace (Visibility Channel)
  │
  ├─ Hit → 壁の法線をチェック（垂直に近いか）
  │         └─ Abs(ImpactNormal.Z) < 0.1 → 壁として有効
  │
  └─ No Hit → 壁なし
```

### 6.2 頂上検出（CheckForLedge）

```
Start: GetActorLocation() + LedgeTraceOffset (頭上 + 数十cm)
Direction: WallNormal * -1 (壁に向かう方向)
End: Start + Direction * LedgeTraceLength

Line Trace (Visibility Channel)
  │
  ├─ Hit → まだ壁がある → bIsAtLedge = false
  │
  └─ No Hit → 壁を見失った → bIsAtLedge = true
                              → OnLedgeReached 発火
```

### 6.3 G キー処理（HandleReleaseInput）

```
HandleReleaseInput:
  │
  ├─ if bIsAtLedge == true
  │     └─ LedgeClimb()
  │           ├─ Play Ledge Climb Animation (Montage)
  │           ├─ Move Character to Ledge Top
  │           ├─ Set Movement Mode (Walking)
  │           ├─ Remove Mapping Context (IMC_Climbing)
  │           ├─ DisableAllClimbingTicks
  │           └─ CallOnClimbingStopped
  │
  └─ else
        └─ ReleaseFromWall()
              ├─ Set Movement Mode (Walking)
              ├─ Remove Mapping Context (IMC_Climbing)
              ├─ DisableAllClimbingTicks
              └─ CallOnClimbingStopped
```

### 6.4 壁吸着位置更新（UpdateWallAttachment - Tick）

```
UpdateWallAttachment (Every Frame):
  │
  ├─ CheckForLedge()  // 頂上検出
  │
  ├─ CurrentLocation = GetActorLocation()
  ├─ TargetLocation = WallHitLocation
  ├─ NewLocation = VInterpTo(Current, Target, DeltaTime, InterpSpeed)
  │
  ├─ CurrentRotation = GetActorRotation()
  ├─ NewRotation = RInterpTo(Current, TargetWallRotation, DeltaTime, InterpSpeed)
  │
  ├─ SetActorLocation(NewLocation)
  └─ SetActorRotation(NewRotation)
```

---

## 7. GASP 連携

### 7.1 Animation Blueprint 連携

| AC_Climbing イベント | ABP 処理 |
|---------------------|----------|
| OnClimbingStarted | StartClimbing_GASP → Climbing ステートへ遷移 |
| OnClimbingStopped | StopClimbing_GASP → 通常ステートへ遷移 |

### 7.2 アニメーション

| 状態 | アニメーション |
|------|----------------|
| WallClimbing Idle | 壁につかまっている待機 |
| WallClimbing Move | 壁を登る/移動 |
| LedgeClimbing | 頂上に登るモンタージュ |

---

## 8. テスト仕様

### 8.1 壁吸着テスト

| テストケース | 期待結果 |
|--------------|----------|
| 壁の前で F キー | 壁に吸着、Movement Mode = Flying |
| 壁がない場所で F キー | 何も起こらない |
| ジャンプ中に F キー | 何も起こらない |
| 既に壁吸着中に F キー | 何も起こらない |

### 8.2 壁移動テスト

| テストケース | 期待結果 |
|--------------|----------|
| 壁吸着中に W キー | 上に移動 |
| 壁吸着中に S キー | 下に移動 |
| 壁吸着中に A/D キー | 左右に移動 |
| 壁の端に到達 | それ以上移動しない |

### 8.3 壁離脱テスト

| テストケース | 期待結果 |
|--------------|----------|
| 壁吸着中（頂上未到達）に G キー | 壁から離脱、落下 |
| 通常状態で G キー | 何も起こらない |

### 8.4 頂上登りテスト

| テストケース | 期待結果 |
|--------------|----------|
| 壁の上端まで登り、G キー | 頂上に登って立つ |
| 頂上到達前に G キー | 壁離脱（頂上登りではない） |

---

## 9. 実装チェックリスト

### Phase 1: 基本機能（現在進行中）
- [x] ABP Climbing ステート追加
- [x] OnClimbingStarted/Stopped イベントバインディング
- [x] StartClimbing_GASP/StopClimbing_GASP 接続
- [x] IA_GrabWall (Fキー) を IMC_Sandbox に追加
- [x] TryGrabWall に Set Movement Mode (Flying) 追加
- [x] Trace Line 方向を Control Rotation から取得
- [ ] BeginPlay から IMC_Climbing の Add Mapping Context を削除
- [ ] TryGrabWall に Add Mapping Context (IMC_Climbing) 追加
- [ ] ReleaseFromWall に Remove Mapping Context 追加
- [ ] ReleaseFromWall に Set Movement Mode (Walking) 追加
- [ ] CBP_SandboxCharacter に IA_Release イベントハンドラー追加
- [ ] 壁吸着・離脱の動作テスト

### Phase 2: 壁移動
- [ ] IA_ClimbMove の入力処理実装
- [ ] HandleClimbInput 関数実装
- [ ] 壁移動の動作テスト

### Phase 3: 頂上登り
- [ ] CheckForLedge 関数実装
- [ ] bIsAtLedge フラグ管理
- [ ] LedgeClimb 関数実装
- [ ] HandleReleaseInput（コンテキスト依存処理）実装
- [ ] Ledge Climb アニメーション連携
- [ ] 頂上登りの動作テスト

---

## 10. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2026-01-27 | 1.0 | 初版作成 - SDD 仕様書 |

---

## 11. 用語集

| 用語 | 説明 |
|------|------|
| GASP | Game Animation Sample Plugin |
| IMC | Input Mapping Context |
| IA | Input Action |
| ABP | Animation Blueprint |
| Ledge | 壁の頂上/縁 |
| Wall Attach | 壁に吸着する動作 |
| Wall Climb | 壁を登る/移動する動作 |
| Wall Release | 壁から離脱する動作 |
| Ledge Climb | 壁の頂上に登る動作 |
