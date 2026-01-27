# AthleticTrial - SPEC.md
# 仕様駆動開発（SDD）仕様書

> **このファイルは「唯一の真実源泉（Single Source of Truth）」です。**
> すべてのコード、テスト、ドキュメントはこの仕様に基づいて作成・更新されます。

---

## 1. プロジェクト概要

### 1.1 目的
AnimationTestProject から AthleticTrial へプレイヤーキャラクターの挙動を移行し、GASP（Game Animation Sample Plugin）と統合したアクションゲームを作成する。

### 1.2 移行元プロジェクト
- **AnimationTestProject**: `C:\Users\work0\uechi\UEProjects\AnimationTestProject`

### 1.3 ベースプロジェクト
- **Game Animation Sample**: [Fab リンク](https://www.fab.com/ja/listings/880e319a-a59e-4ed2-b268-b32dac7fa016)

### 1.4 環境
| 項目 | 値 |
|------|-----|
| OS | Windows 11 |
| Unreal Engine | 5.5.4 |
| Graphics API | DirectX 12 |
| Shader Model | SM6 |

### 1.5 関連ドキュメント
| ドキュメント | 説明 |
|-------------|------|
| [ProjectStructure.md](Docs/Design/ProjectStructure.md) | プロジェクト構造（アセット一覧、フォルダ構成） |
| [ClimbingSystem_SDD.md](Docs/Design/ClimbingSystem_SDD.md) | クライミングシステム詳細設計 |
| [ClimbingSystem_InputDesign.md](Docs/Design/ClimbingSystem_InputDesign.md) | 入力設計詳細 |

---

## 2. 機能仕様

### 2.1 クライミングシステム

#### 2.1.1 壁吸着（Wall Attach）

**概要**: プレイヤーが壁に向かって F キーを押すと、壁に吸着する。

**受け入れ基準**:
```gherkin
Feature: 壁吸着
  Scenario: 壁の前で F キーを押す
    Given プレイヤーが壁の前に立っている
    And プレイヤーはクライミング中ではない
    And プレイヤーは落下中ではない
    When プレイヤーが F キーを押す
    Then プレイヤーが壁に吸着する
    And Movement Mode が Flying になる
    And IMC_Climbing が有効になる
    And OnClimbingStarted イベントが発火する

  Scenario: 壁がない場所で F キーを押す
    Given プレイヤーの前に壁がない
    When プレイヤーが F キーを押す
    Then 何も起こらない

  Scenario: ジャンプ中に F キーを押す
    Given プレイヤーがジャンプ中（落下中）
    When プレイヤーが F キーを押す
    Then 何も起こらない
```

**技術仕様**:
| 項目 | 値 |
|------|-----|
| トリガー | F キー (IA_GrabWall) |
| 壁検出 | Line Trace (Control Rotation Forward, TraceLength) |
| 壁判定 | Abs(ImpactNormal.Z) < 0.1 |
| 吸着位置 | ImpactPoint + (WallNormal * WallOffset) |
| WallOffset デフォルト | 60.0 |

#### 2.1.2 壁移動（Wall Climb）

**概要**: 壁吸着中に WASD キーで壁の表面を移動する。

**受け入れ基準**:
```gherkin
Feature: 壁移動
  Scenario: 壁吸着中に W キーを押す
    Given プレイヤーが壁に吸着している
    When プレイヤーが W キーを押し続ける
    Then プレイヤーが上方向に移動する

  Scenario: 壁吸着中に S キーを押す
    Given プレイヤーが壁に吸着している
    When プレイヤーが S キーを押し続ける
    Then プレイヤーが下方向に移動する

  Scenario: 壁吸着中に A/D キーを押す
    Given プレイヤーが壁に吸着している
    When プレイヤーが A または D キーを押し続ける
    Then プレイヤーが左右に移動する

  Scenario: 壁の端に到達
    Given プレイヤーが壁に吸着している
    And プレイヤーが壁の端にいる
    When プレイヤーが壁の外方向に移動しようとする
    Then プレイヤーはそれ以上移動しない
```

**技術仕様**:
| 項目 | 値 |
|------|-----|
| トリガー | WASD キー (IA_ClimbUp) |
| 移動方向 | 壁の法線に対して垂直方向 |
| 移動速度 | ClimbSpeed 変数で制御 |
| 入力処理 | SetClimbInput(Horizontal, Vertical) で 2軸入力 |

#### 2.1.3 壁離脱（Wall Release）

**概要**: 壁吸着中に G キーを押すと、壁から離脱する（頂上未到達時）。

**受け入れ基準**:
```gherkin
Feature: 壁離脱
  Scenario: 壁吸着中（頂上未到達）に G キーを押す
    Given プレイヤーが壁に吸着している
    And プレイヤーは頂上に到達していない (bIsAtLedge == false)
    When プレイヤーが G キーを押す
    Then プレイヤーが壁から離脱する
    And Movement Mode が Walking になる
    And IMC_Climbing が無効になる
    And OnClimbingStopped イベントが発火する
    And プレイヤーが落下する

  Scenario: 通常状態で G キーを押す
    Given プレイヤーが通常状態（壁吸着していない）
    When プレイヤーが G キーを押す
    Then 何も起こらない
```

**技術仕様**:
| 項目 | 値 |
|------|-----|
| トリガー | G キー (IA_Release) |
| 条件 | bIsClimbing == true AND bIsAtLedge == false |

#### 2.1.4 頂上登り（Ledge Climb）

**概要**: 壁の頂上に到達した状態で G キーを押すと、壁の上に登って立つ。

**受け入れ基準**:
```gherkin
Feature: 頂上登り
  Scenario: 壁の頂上に到達後、G キーを押す
    Given プレイヤーが壁に吸着している
    And プレイヤーが頂上に到達している (bIsAtLedge == true)
    When プレイヤーが G キーを押す
    Then Ledge Climb アニメーションが再生される
    And プレイヤーが壁の上に移動する
    And Movement Mode が Walking になる
    And IMC_Climbing が無効になる
    And OnClimbingStopped イベントが発火する

  Scenario: 頂上検出
    Given プレイヤーが壁に吸着している
    And プレイヤーが上方向に移動している
    When 頭上オフセット位置からの Line Trace が壁を見失う
    Then bIsAtLedge が true になる
    And OnLedgeReached イベントが発火する
```

**技術仕様**:
| 項目 | 値 |
|------|-----|
| トリガー | G キー (IA_Release) |
| 条件 | bIsClimbing == true AND bIsAtLedge == true |
| 頂上検出 | 頭上 + LedgeTraceOffset から Line Trace |
| 頂上判定 | Line Trace が壁を見失った場合 |

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
| IA_ClimbUp | WASD | 壁移動（SetClimbInput で処理） |
| IA_Release | G | 壁離脱 / 頂上登り（コンテキスト依存） |
| IA_Look | マウス | カメラ操作 |

### 3.3 G キーのコンテキスト依存動作

```
G キー押下時:
  if bIsAtLedge == true:
    → LedgeClimb()      // 頂上に登る
  else:
    → ReleaseFromWall() // 壁離脱
```

---

## 4. 状態遷移

### 4.1 状態定義

| 状態 | 説明 | Movement Mode | IMC_Climbing |
|------|------|---------------|--------------|
| Normal | 通常状態 | Walking | 無効 |
| WallClimbing | 壁吸着中 | Flying | 有効 |
| LedgeReached | 頂上到達（壁吸着中） | Flying | 有効 |
| LedgeClimbing | 頂上登り中 | Flying | 有効 |

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
| 変数名 | 型 | デフォルト | 説明 |
|--------|-----|------------|------|
| bIsClimbing | bool | false | クライミング中フラグ |
| bIsWallClimbingActive | bool | false | 壁クライミング Tick 有効フラグ |
| bIsLedgeClimbingActive | bool | false | Ledge クライミング Tick 有効フラグ |
| bIsAtLedge | bool | false | 頂上到達フラグ |
| WallNormal | Vector | (0,0,0) | 壁の法線ベクトル |
| WallHitLocation | Vector | (0,0,0) | 壁のヒット位置（オフセット込み） |
| TargetWallRotation | Rotator | (0,0,0) | 壁に向かう目標回転 |
| WallOffset | float | 60.0 | 壁からのオフセット距離 |
| TraceLength | float | 200.0 | Line Trace の長さ |
| LedgeTraceOffset | Vector | (0,0,100) | 頂上検出用 Trace のオフセット |
| LocationInterpSpeed | float | 100.0 | 位置補間速度 |
| RotationInterpSpeed | float | 100.0 | 回転補間速度 |

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
| SetClimbInput | 壁移動入力処理（Horizontal, Vertical） |
| HandleReleaseInput | G キー入力処理（コンテキスト依存） |

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
| IA_Release (Started) | HandleReleaseInput |
| IA_ClimbUp | SetClimbInput（AC_Climbing 経由） |

---

## 6. GASP 連携

### 6.1 Animation Blueprint 連携

| AC_Climbing イベント | ABP 処理 |
|---------------------|----------|
| OnClimbingStarted | StartClimbing_GASP → Climbing ステートへ遷移 |
| OnClimbingStopped | StopClimbing_GASP → 通常ステートへ遷移 |

### 6.2 アニメーション

| 状態 | アニメーション |
|------|----------------|
| WallClimbing Idle | 壁につかまっている待機 |
| WallClimbing Move | 壁を登る/移動 |
| LedgeClimbing | 頂上に登るモンタージュ |

---

## 7. 実装チェックリスト

### Phase 1: 基本機能

**注記**: IMC 切り替えと Movement Mode 変更は、AC_Climbing の TryGrabWall/ReleaseFromWall ではなく、
CBP_SandboxCharacter の **StartClimbing_GASP/StopClimbing_GASP** で実装されています。

- [x] ABP Climbing ステート追加
- [x] OnClimbingStarted/Stopped イベントバインディング
- [x] StartClimbing_GASP/StopClimbing_GASP 接続
- [x] IA_GrabWall (Fキー) を IMC_Sandbox に追加
- [x] TryGrabWall に Set Movement Mode (Flying) 追加
- [x] Trace Line 方向を Control Rotation から取得
- [x] Add Mapping Context (IMC_Climbing) - **StartClimbing_GASP で実装済み**
- [x] Remove Mapping Context (IMC_Climbing) - **StopClimbing_GASP で実装済み**
- [x] Set Movement Mode (Walking) - **StopClimbing_GASP で実装済み**
- [ ] BeginPlay から IMC_Climbing の Add Mapping Context を削除（不要な初期化）
- [ ] CBP_SandboxCharacter に IA_Release イベントハンドラー追加
- [ ] 壁吸着・離脱の動作テスト

### Phase 2: 壁移動
- [ ] IA_ClimbUp の入力処理実装（IMC_Climbing にマッピング）
- [ ] SetClimbInput 関数連携（AC_Climbing）
- [ ] 壁移動の動作テスト

### Phase 3: 頂上登り

**注記**: AC_Climbing では SPEC.md と異なる命名で実装されています。

| SPEC.md | AC_Climbing 実装 |
|---------|------------------|
| bIsAtLedge | bIsAtClimbTop |
| CheckForLedge | IsAtClimbTop |
| LedgeClimb | StartClimbUpTop |

- [x] CheckForLedge 関数実装 - **IsAtClimbTop として実装済み**（頭上+100cmからLine Trace）
- [x] bIsAtLedge フラグ管理 - **bIsAtClimbTop として実装済み**（Event Tick で自動更新）
- [x] LedgeClimb 関数実装 - **StartClimbUpTop として実装済み**
- [x] Ledge Climb アニメーション連携 - **AM_ClimbUp_At_Top モンタージュ連携済み**
- [ ] HandleReleaseInput（コンテキスト依存処理）実装 - **CBP_SandboxCharacter に IA_Release ハンドラー追加が必要**
- [ ] 頂上登りの動作テスト

---

## 8. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2026-01-27 | 1.0 | 初版作成 - クライミングシステム仕様 |
| 2026-01-27 | 1.1 | IA_ClimbMove → IA_ClimbUp に修正（実プロジェクトとの整合性） |
| 2026-01-27 | 1.2 | Phase 1 チェックリスト更新 - IMC 切り替え実装場所を StartClimbing_GASP/StopClimbing_GASP に明記 |
| 2026-01-27 | 1.3 | Phase 3 チェックリスト更新 - AC_Climbing 実装との命名対応表追加、実装済み項目を完了マーク |

---

## 9. 用語集

| 用語 | 説明 |
|------|------|
| SDD | Spec-Driven Development（仕様駆動開発） |
| GASP | Game Animation Sample Plugin |
| IMC | Input Mapping Context |
| IA | Input Action |
| ABP | Animation Blueprint |
| Ledge | 壁の頂上/縁 |
| Wall Attach | 壁に吸着する動作 |
| Wall Climb | 壁を登る/移動する動作 |
| Wall Release | 壁から離脱する動作 |
| Ledge Climb | 壁の頂上に登る動作 |
