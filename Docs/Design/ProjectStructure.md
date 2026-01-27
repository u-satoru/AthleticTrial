# AthleticTrial - プロジェクト構造ドキュメント

## 概要

このドキュメントは、AthleticTrial プロジェクトの Unreal Engine アセット構造を定義します。

---

## 1. 主要フォルダ構造

```
/Game/
├── Blueprints/                          # メインBlueprint
│   ├── CBP_SandboxCharacter             # プレイヤーキャラクター
│   ├── ABP_SandboxCharacter             # Animation Blueprint
│   ├── GM_Sandbox                       # Game Mode
│   └── ...
│
├── ThirdPerson/                         # サードパーソン関連
│   ├── Blueprints/
│   │   ├── Components/
│   │   │   └── AC_Climbing              # クライミングコンポーネント
│   │   └── Enums/
│   │       └── E_ClimbState             # クライミング状態Enum
│   ├── Input/
│   │   ├── IMC_Climbing                 # クライミング用IMC（壁吸着中のみ有効）
│   │   └── Actions/
│   │       ├── IA_GrabWall              # 壁吸着アクション (F)
│   │       ├── IA_Release               # 壁離脱アクション (G)
│   │       ├── IA_ClimbUp               # 壁移動アクション (WASD)
│   │       └── ...
│
├── Input/                               # 通常操作用
│   ├── IMC_Sandbox                      # 通常操作用IMC（常時有効）
│   └── ...
│   └── Maps/
│       └── ThirdPersonMap               # メインレベル
│
├── Characters/                          # キャラクターアセット
│   └── Mannequins/
│       └── Animations/
│
├── GameAnimationSample/                 # GASP関連
│   ├── Characters/
│   ├── Animation/
│   └── ...
│
├── FreeAnimationLibrary/                # 外部アニメーションライブラリ
│
├── StarterContent/                      # UE標準コンテンツ
│
└── LevelPrototyping/                    # レベルプロトタイピング
```

---

## 2. クライミングシステム関連アセット

### 2.1 Blueprint

| アセット名 | パス | 説明 |
|-----------|------|------|
| CBP_SandboxCharacter | /Game/Blueprints/ | プレイヤーキャラクター |
| ABP_SandboxCharacter | /Game/Blueprints/ | Animation Blueprint |
| AC_Climbing | /Game/ThirdPerson/Blueprints/Components/ | クライミングコンポーネント |

### 2.2 Enum

| アセット名 | パス | 値 |
|-----------|------|-----|
| E_ClimbState | /Game/ThirdPerson/Blueprints/Enums/ | Idle, Moving, Grabbing, ClimbingUp, Jumping, Releasing |

### 2.3 Input

| アセット名 | パス | 説明 |
|-----------|------|------|
| IMC_Sandbox | /Game/Input/ | 通常操作用（Priority: 0、常時有効） |
| IMC_Climbing | /Game/ThirdPerson/Input/ | クライミング用（Priority: 1、壁吸着中のみ） |
| IA_GrabWall | /Game/ThirdPerson/Input/Actions/ | Fキー - 壁吸着 |
| IA_Release | /Game/ThirdPerson/Input/Actions/ | Gキー - 壁離脱/頂上登り |
| IA_ClimbUp | /Game/ThirdPerson/Input/Actions/ | WASDキー - 壁移動（SetClimbInput で処理） |

---

## 3. GASP（Game Animation Sample Plugin）関連

### 3.1 主要アセット

| カテゴリ | パス |
|----------|------|
| キャラクター | /Game/GameAnimationSample/Characters/ |
| アニメーション | /Game/GameAnimationSample/Animation/ |
| Locomotion | /Game/GameAnimationSample/Animation/Locomotion/ |

### 3.2 Animation Blueprint 連携

| AC_Climbing イベント | ABP 処理 |
|---------------------|----------|
| OnClimbingStarted | StartClimbing_GASP → Climbing ステートへ遷移 |
| OnClimbingStopped | StopClimbing_GASP → 通常ステートへ遷移 |

---

## 4. コンポーネント依存関係

```
CBP_SandboxCharacter
    │
    ├── AC_Climbing (Actor Component)
    │       │
    │       ├── Event Dispatcher
    │       │   ├── OnClimbingStarted
    │       │   ├── OnClimbingStopped
    │       │   └── OnLedgeReached
    │       │
    │       └── 参照
    │           ├── IMC_Climbing
    │           ├── E_ClimbState
    │           └── Character Movement Component
    │
    └── ABP_SandboxCharacter (Animation Blueprint)
            │
            └── Climbing State Machine
                ├── Idle
                ├── Moving
                └── LedgeClimbing
```

---

## 5. Input Mapping Context 構造

### 5.1 IMC_Sandbox（常時有効）

| Input Action | キー | 説明 |
|-------------|------|------|
| IA_Move | WASD | 通常移動 |
| IA_Look | マウス | カメラ操作 |
| IA_Jump | Space | ジャンプ |
| IA_GrabWall | F | 壁吸着開始 |

### 5.2 IMC_Climbing（壁吸着中のみ有効）

| Input Action | キー | 説明 |
|-------------|------|------|
| IA_ClimbUp | WASD | 壁移動（SetClimbInput で処理） |
| IA_Release | G | 壁離脱 / 頂上登り |
| IA_Look | マウス | カメラ操作 |

---

## 6. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2026-01-27 | 1.0 | 初版作成 |
| 2026-01-27 | 1.1 | IMC_Sandbox パス修正、IA_ClimbUp 説明更新 |

