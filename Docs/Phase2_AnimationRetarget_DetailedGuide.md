# Phase 2: アニメーションリターゲット基盤構築 - 詳細手順書

**バージョン**: 3.0 (UE 5.5.4 実証済み・Phase 2 完了)
**作成日**: 2026-01-21
**更新日**: 2026-01-21
**対象**: AthleticTrial プロジェクト (UE 5.5.4)

---

## 0. 概要

### 目的
FreeAnimationLibrary (133個) と FreeSampleAnimationSet (182個) のアニメーションを、GASP の UEFN_Mannequin スケルトンで使用可能にする。

### 前提条件
- AthleticTrial プロジェクトが起動可能
- FreeAnimationLibrary と FreeSampleAnimationSet が `Content/` にコピー済み ✅
- Unreal Editor での GUI 操作が可能
- **Unreal Engine 5.5.4** を使用

### 作業時間目安
- Step 1 (IK Rig 作成): 10-15分 ※Auto Retarget Chains で大幅短縮
- Step 2 (Retargeter 作成): 10-15分
- Step 3 (バッチリターゲット): 30-60分（アニメーション数による）
- Step 4 (検証): 15-20分

---

## 1. 現状分析

### 1.1 スケルトン構成

| カテゴリ | スケルトン | パス | 用途 |
|---------|-----------|------|------|
| **ソース（変換元）** | SK_Mannequin | `/Game/FreeSampleAnimationSet/Demo/Mannequin_UE4/Meshes/` | アニメーションライブラリ用（UE4スケルトン） |
| **ターゲット（変換先）** | SK_UEFN_Mannequin | `/Game/Characters/UEFN_Mannequin/Meshes/` | GASP メインスケルトン |

> **⚠️ 重要な発見**: FreeAnimationLibrary のアニメーションは、FreeAnimationLibrary/Demo/Characters/ にある SK_Mannequin ではなく、**FreeSampleAnimationSet/Demo/Mannequin_UE4/** にある SK_Mannequin（UE4スケルトン）を参照しています。これは両ライブラリが同じスケルトンを共有しているためです。

### 1.2 既存の IK Rig / Retargeter

| アセット | パス | 状態 |
|---------|------|------|
| IK_UEFN_Mannequin | `/Game/Characters/UEFN_Mannequin/Rigs/` | ✅ 存在（ターゲット用） |
| IK_UE5_Mannequin_Retarget | `/Game/Characters/UE5_Mannequins/Rigs/` | ✅ 存在（参考用） |
| RTG_UEFN_to_UE5_Mannequin | `/Game/Characters/UE5_Mannequins/Rigs/` | ✅ 存在（参考用） |
| **IK_FreeAnimationLibrary** | `/Game/FreeAnimationLibrary/Animations/Rigs/` | ✅ **既存（ソース用）** |
| **RTG_FreeAnim_to_UEFN** | - | ❌ **新規作成が必要** |

### 1.3 リターゲット方向

```
[ソース]                              [ターゲット]
SK_Mannequin                    →     SK_UEFN_Mannequin
(FreeAnimationLibrary用)              (GASP用)
       ↓                                    ↓
IK_FreeAnimationLibrary         →     IK_UEFN_Mannequin
(新規作成)                              (既存)
              ↘               ↙
              RTG_FreeAnim_to_UEFN
                 (新規作成)
```

---

## 2. Step 1: ソース用 IK Rig 作成（UE 5.5.4 手順）

### 2.1 IK Rig 作成手順（UE 5.5+ 対応）

> **重要**: UE 5.5 では、IK Rig はスケルタルメッシュの右クリックメニューからではなく、Content Browser の「Add (+)」ボタンから作成します。

1. **Content Browser を開く**
   - 保存先フォルダに移動: `/Game/FreeAnimationLibrary/Rigs/`
   - （Rigs フォルダがなければ右クリック → New Folder で作成）

2. **IK Rig を作成**
   ```
   ┌─────────────────────────────────────────────────────────────┐
   │  Content Browser 左上の緑色「+ Add」ボタンをクリック         │
   │                    ↓                                        │
   │  「Animation」カテゴリを展開                                  │
   │                    ↓                                        │
   │  「Retargeting」サブカテゴリを展開                            │
   │                    ↓                                        │
   │  「IK Rig」を選択                                            │
   └─────────────────────────────────────────────────────────────┘
   ```

3. **スケルタルメッシュを選択**

   > **⚠️ 重要**: プロジェクト内には同名の `SK_Mannequin` が複数存在します。
   > **必ずパスを確認**して正しいものを選択してください。
   >
   > **✅ 既存の IK Rig を使用**: `/Game/FreeAnimationLibrary/Animations/Rigs/IK_FreeAnimationLibrary` が既に存在し、正しいスケルトンで設定済みです。新規作成せずにこれを使用してください。

   ```
   ダイアログまたは IK Rig エディタの Preview Mesh 設定で:

   1. 検索欄に「SK_Mannequin」と入力
   2. 複数の候補が表示されるので、パスを確認:

      ✅ 正解: /Game/FreeSampleAnimationSet/Demo/Mannequin_UE4/Meshes/SK_Mannequin
      ❌ 不正解: /Game/FreeAnimationLibrary/Demo/Characters/Mannequins/Meshes/SK_Mannequin
      ❌ 不正解: /Game/FreeSampleAnimationSet/Demo/Mannequins/Meshes/SK_Mannequin
      ❌ 不正解: /Game/Characters/UE5_Mannequins/Meshes/SK_Mannequin

   3. FreeSampleAnimationSet/Demo/Mannequin_UE4 内の SK_Mannequin を選択
      （FreeAnimationLibrary のアニメーションが実際に参照しているスケルトン）
   4. 「Create」または「OK」をクリック（ダイアログの場合）
   ```

   > **💡 確認方法**: 選択後、Details パネルで Skeleton パスが
   > `/Game/FreeSampleAnimationSet/Demo/Mannequin_UE4/Meshes/`
   > で始まっていることを確認

4. **アセット名を設定**
   - 名前: `IK_FreeAnimationLibrary`
   - 保存先: `/Game/FreeAnimationLibrary/Rigs/`

### 2.2 Auto Retarget Chains を使用（推奨・UE 5.5 新機能）

> **UE 5.5 の Auto Retarget Chains ツール**により、IK チェーンを自動生成できます。これにより手動設定が大幅に省略できます。

1. **IK Rig エディタを開く**
   - Content Browser で `IK_FreeAnimationLibrary` をダブルクリック

2. **Auto Retarget Chains を実行**
   ```
   ┌─────────────────────────────────────────────────────────────┐
   │  IK Rig エディタのツールバーにある                           │
   │  「Auto Retarget Chains」ボタンをクリック                    │
   │                                                             │
   │  ツールがスケルトンの構造を自動解析し、                       │
   │  以下を自動設定します:                                       │
   │  - Retarget Root (pelvis)                                   │
   │  - Spine Chain                                              │
   │  - Head/Neck Chain                                          │
   │  - Left/Right Arm Chains                                    │
   │  - Left/Right Leg Chains                                    │
   └─────────────────────────────────────────────────────────────┘
   ```

3. **自動生成結果の確認**
   - 通知ウィンドウに結果が表示される
   - 警告やエラーがあれば対処（後述）

4. **保存**
   - `Ctrl + S` で保存

### 2.3 手動設定（Auto Retarget Chains が失敗した場合）

Auto Retarget Chains でチェーンが正しく生成されなかった場合のみ、以下の手動手順を実行します。

#### A. Retarget Root の設定（最重要）

```
1. 左側の「Hierarchy」パネルで「pelvis」ボーンを見つける
2. pelvis を右クリック
3. 「Set Retarget Root」を選択
   → pelvis の横に [Root] マークが表示される
```

#### B. IK Chain の手動作成

各チェーンの作成手順:

```
1. Hierarchy パネルで開始ボーンをクリック
2. Shift キーを押しながら終端ボーンをクリック（範囲選択）
3. 右クリック → 「New Retarget Chain from Selected Bones」
4. チェーン名を入力して確定
```

| チェーン名 | 開始ボーン | 終端ボーン | 備考 |
|-----------|-----------|-----------|------|
| **Spine** | spine_01 | spine_05 | 背骨全体 |
| **Head** | neck_01 | head | 首から頭 |
| **LeftArm** | clavicle_l | hand_l | 鎖骨から手 |
| **RightArm** | clavicle_r | hand_r | 鎖骨から手 |
| **LeftLeg** | thigh_l | foot_l | 太ももから足 |
| **RightLeg** | thigh_r | foot_r | 太ももから足 |

#### C. ボーン名参照（SK_Mannequin）

```
[Root/Pelvis - Retarget Root として設定]
pelvis

[Spine Chain]
spine_01 → spine_02 → spine_03 → spine_04 → spine_05

[Head Chain]
neck_01 → neck_02 → head

[Left Arm Chain]
clavicle_l → upperarm_l → lowerarm_l → hand_l
  └─ [Fingers] index_01_l, middle_01_l, ring_01_l, pinky_01_l, thumb_01_l

[Right Arm Chain]
clavicle_r → upperarm_r → lowerarm_r → hand_r
  └─ [Fingers] index_01_r, middle_01_r, ring_01_r, pinky_01_r, thumb_01_r

[Left Leg Chain]
thigh_l → calf_l → foot_l → ball_l

[Right Leg Chain]
thigh_r → calf_r → foot_r → ball_r
```

### 2.4 確認ポイント

- [ ] Retarget Root が pelvis に設定されている（[Root] マーク表示）
- [ ] 6つのチェーン（Spine, Head, LeftArm, RightArm, LeftLeg, RightLeg）が作成されている
- [ ] 各チェーンのボーン範囲が正しい
- [ ] IK Rig が保存されている

---

## 3. Step 2: IK Retargeter 作成（UE 5.5.4 手順）

### 3.1 Retargeter 作成手順

1. **Content Browser で保存先に移動**
   - 場所: `/Game/FreeAnimationLibrary/Rigs/`

2. **IK Retargeter を作成**
   ```
   ┌─────────────────────────────────────────────────────────────┐
   │  Content Browser 左上の緑色「+ Add」ボタンをクリック         │
   │                    ↓                                        │
   │  「Animation」カテゴリを展開                                  │
   │                    ↓                                        │
   │  「Retargeting」サブカテゴリを展開                            │
   │                    ↓                                        │
   │  「IK Retargeter」を選択                                     │
   └─────────────────────────────────────────────────────────────┘
   ```

3. **Source IK Rig を選択**
   ```
   ダイアログで:
   - IK_FreeAnimationLibrary を選択（Step 1 で作成したもの）
   - 「Create」または「OK」をクリック
   ```

4. **名前を設定**
   - 名前: `RTG_FreeAnim_to_UEFN`

### 3.2 Retargeter エディタでの設定

1. **IK Retargeter エディタを開く**
   - Content Browser で `RTG_FreeAnim_to_UEFN` をダブルクリック

2. **Target IK Rig を設定**
   ```
   ┌─────────────────────────────────────────────────────────────┐
   │  右側の Details パネルで:                                    │
   │                                                             │
   │  「Target IKRig Asset」項目を見つける                        │
   │                    ↓                                        │
   │  ドロップダウンまたはピッカーで                               │
   │  「IK_UEFN_Mannequin」を選択                                 │
   │                                                             │
   │  パス: /Game/Characters/UEFN_Mannequin/Rigs/IK_UEFN_Mannequin│
   └─────────────────────────────────────────────────────────────┘
   ```

3. **Chain Mapping を確認**

   中央の「Chain Mapping」パネルで自動マッピング状況を確認:

   | Source Chain | Target Chain | 期待状態 |
   |--------------|--------------|----------|
   | Spine | Spine | ✅ 自動マッピング |
   | Head | Head | ✅ 自動マッピング |
   | LeftArm | LeftArm | ✅ 自動マッピング |
   | RightArm | RightArm | ✅ 自動マッピング |
   | LeftLeg | LeftLeg | ✅ 自動マッピング |
   | RightLeg | RightLeg | ✅ 自動マッピング |

4. **マッピングの修正（必要な場合）**
   ```
   マッピングされていないチェーンがある場合:

   1. Chain Mapping パネルで該当行を見つける
   2. 「Source Chain」列のドロップダウンをクリック
   3. 対応するソースチェーンを選択

   または:
   1. 「Auto-Map Chains」ボタン（ある場合）をクリック
   ```

### 3.3 Root Settings の確認

1. **Root Settings を開く**
   ```
   Chain Mapping パネル上部の「Root Settings」ボタンをクリック
   または
   ビューポートで Root（骨盤）のビジュアライザーを選択
   ```

2. **推奨設定**
   ```
   [Root Settings]
   - Rotation Alpha: 1.0（デフォルト）
   - Translation Alpha: 1.0（デフォルト）
   - Blend to Source: 0.0（デフォルト）
   - Affect IK Horizontal: true
   - Affect IK Vertical: true
   ```

### 3.4 Retargeter のテスト

1. **Preview でアニメーションを確認**
   ```
   1. エディタ下部の「Asset Browser」パネルを表示
      （見えない場合は Window → Asset Browser）

   2. /Game/FreeAnimationLibrary/Animations/ に移動

   3. 任意のアニメーションをダブルクリックまたはドラッグ

   4. プレビューウィンドウで:
      - 左側: Source キャラクター（SK_Mannequin）
      - 右側: Target キャラクター（SK_UEFN_Mannequin）
      が表示される

   5. 再生ボタンでアニメーションを再生

   6. 両キャラクターのポーズが一致していることを確認
   ```

2. **問題がある場合の調整**

   | 症状 | 調整箇所 | 設定 |
   |------|---------|------|
   | ポーズ全体がずれる | Root Settings | Translation/Rotation Alpha を調整 |
   | 手足の位置がずれる | Root Settings | Blend to Source を 0.2〜0.5 に |
   | 特定チェーンがおかしい | Chain Settings | 該当チェーンの FK/IK Blend を調整 |

### 3.5 確認ポイント

- [ ] Source IK Rig が `IK_FreeAnimationLibrary` になっている
- [ ] Target IK Rig が `IK_UEFN_Mannequin` になっている
- [ ] 全チェーンがマッピングされている（未マッピングなし）
- [ ] プレビューでポーズが正しく変換されている
- [ ] Retargeter が保存されている

---

## 4. Step 3: バッチリターゲット実行

### 4.1 リターゲット対象の確認

| ライブラリ | アニメーション数 | ソースパス |
|-----------|-----------------|-----------|
| FreeAnimationLibrary | 133 | `/Game/FreeAnimationLibrary/Animations/` |
| FreeSampleAnimationSet | 182 | `/Game/FreeSampleAnimationSet/Animations/` |
| **合計** | **315** | - |

### 4.2 出力先フォルダの作成

> **注意**: リターゲット時に「Flatten Folder Structure」をオフにすると、元のサブフォルダ構造が自動的に維持されます。手動でフォルダを作成する必要はありません。

```
リターゲット後の出力先（自動生成）:

/Game/Characters/UEFN_Mannequin/Animations/Retargeted/
├── FreeAnimationLibrary/
│   ├── Climbing_Animations/
│   │   ├── Climbing/
│   │   ├── Idle/
│   │   ├── WallChange/
│   │   └── WallGrab_unGrab/
│   ├── Counter-Finisher/
│   ├── Cover/
│   ├── Crouch/
│   ├── FallLoop/
│   ├── Idle/
│   ├── Interaction/
│   ├── Jog/
│   ├── Jump/
│   ├── Ladder/
│   ├── LandingRoll/
│   ├── LedgeClimb/
│   ├── Mantle/
│   ├── Pole/
│   ├── Revive/
│   ├── Slide/
│   ├── Stair/
│   ├── Swim/
│   ├── UnarmedProne/
│   ├── Vault/
│   └── Walk/
└── FreeSampleAnimationSet/
    ├── CoverSet/Mannequin/RootMotion/
    ├── DBNOSet/
    ├── DashDodgeRollSet/Mannequin/RootMotion/Roll/
    ├── FemaleLocomotionSet/Mannequin/RootMotion/
    ├── ItemPickupSet/Mannequin/
    ├── LadderSet/Mannequin/RootMotion/
    ├── LiftSet/Mannequin/InPlace/Lightweight/...
    ├── MaleLocomotionSet/Mannequin/RootMotion/
    ├── NarrowPassageSet/Mannequin/RootMotion/...
    ├── PullSet/Mannequin/RootMotion/...
    ├── PushSet/RootMotion/...
    ├── ResourceGatheringSet/Mannequin/...
    ├── StairsSet/Mannequin/RootMotion/...
    ├── StorageUnitsSet/Mannequin/...
    └── SurvivalSet/Mannequin/...
```

> **💡 ヒント**: FreeSampleAnimationSet はネストが深いフォルダ構造を持っています。リターゲット時にこの構造が維持されるため、出力パスを指定する際は親フォルダ（`/Game/Characters/UEFN_Mannequin/Animations/Retargeted/FreeSampleAnimationSet/`）だけを指定すれば OK です。

### 4.3 バッチリターゲット手順（UE 5.5.4 実証済み）

> **⚠️ 重要**: UE 5.5.4 では「Retarget Animation Assets」ではなく「**Retarget Animations**」メニューを使用します。

#### 一括リターゲット手順（実証済み）

```
[全アニメーションを一度にリターゲット]

1. Content Browser で以下に移動:
   /Game/FreeAnimationLibrary/Animations/
   または
   /Game/FreeSampleAnimationSet/Animations/

2. フォルダ内の全アニメーションを選択:
   - Ctrl + A で全選択
   - または Shift + クリックで範囲選択

3. 選択したアニメーションを右クリック

4. メニューから選択:
   「Retarget Animations」  ← ※「Retarget Animation Assets」ではない！

5. Retarget Animations ダイアログが表示されたら設定:
   ┌─────────────────────────────────────────────────────────────┐
   │  Source Skeletal Mesh:                                      │
   │    SK_Mannequin                                             │
   │    (パス: /Game/FreeSampleAnimationSet/Demo/Mannequin_UE4/) │
   │                                                             │
   │  Target Skeletal Mesh:                                      │
   │    SKM_UEFN_Mannequin                                       │
   │    (パス: /Game/Characters/UEFN_Mannequin/Meshes/)          │
   │                                                             │
   │  ☐ Auto Generate Retargeter ← オフにする                   │
   │                                                             │
   │  Retarget Asset:                                            │
   │    RTG_FreeAnim_to_UEFN                                     │
   └─────────────────────────────────────────────────────────────┘

   画面下部に「Ready to export! Select animations to export.」と
   表示されれば設定完了。

6. アニメーションを選択して「Export Animations」をクリック

7. Export Path ダイアログで出力先を設定:
   - 出力先フォルダを選択（例: /Game/Characters/UEFN_Mannequin/Animations/）
   - ☑ Use Source Path をオンにすると元のフォルダ構造が維持される
   - 「Select Folder」をクリック

8. 処理完了を待つ
   - 完了後、Content Browser が自動的に出力先フォルダを表示
   - リターゲット済みアニメーションは末尾に「1」が追加される
     （例: A_JogBwd_Loop → A_JogBwd_Loop1）
```

#### 結果の確認方法

```
[サムネイルによる視覚的確認]

リターゲット完了後、Content Browser で以下を確認:

- オレンジ色のキャラクター = リターゲット済み（UEFN_Mannequin）
- 白/青色のキャラクター = オリジナル（SK_Mannequin）

[Animation Editor での確認]

1. リターゲット済みアニメーションをダブルクリック
2. Animation Editor が開く
3. 確認ポイント:
   - Skeleton: SK_UEFN_Mannequin と表示されている
   - Preview Mesh: オレンジ色のキャラクター（SKM_UEFN_Mannequin）
   - アニメーションが正常に再生される
```

### 4.4 カテゴリ別リターゲット実行

以下の順序で各カテゴリをリターゲットしていきます:

#### FreeAnimationLibrary (21カテゴリ)

| # | カテゴリ | 優先度 | 状態 |
|---|---------|--------|------|
| 1 | Climbing_Animations | ★★★ 最優先 | [ ] |
| 2 | LedgeClimb | ★★★ 最優先 | [ ] |
| 3 | Walk | ★★ 高 | [ ] |
| 4 | Jog | ★★ 高 | [ ] |
| 5 | Jump | ★★ 高 | [ ] |
| 6 | Idle | ★★ 高 | [ ] |
| 7 | FallLoop | ★★ 高 | [ ] |
| 8 | LandingRoll | ★★ 高 | [ ] |
| 9 | Mantle | ★ 中 | [ ] |
| 10 | Vault | ★ 中 | [ ] |
| 11 | Ladder | ★ 中 | [ ] |
| 12 | Crouch | ★ 中 | [ ] |
| 13 | Slide | ★ 中 | [ ] |
| 14 | Cover | ★ 中 | [ ] |
| 15 | Stair | ★ 中 | [ ] |
| 16 | Pole | 低 | [ ] |
| 17 | Swim | 低 | [ ] |
| 18 | UnarmedProne | 低 | [ ] |
| 19 | Revive | 低 | [ ] |
| 20 | Interaction | 低 | [ ] |
| 21 | Counter-Finisher | 低 | [ ] |

#### FreeSampleAnimationSet (15カテゴリ)

| # | カテゴリ | 状態 |
|---|---------|------|
| 1 | MaleLocomotionSet | [ ] |
| 2 | FemaleLocomotionSet | [ ] |
| 3 | LadderSet | [ ] |
| 4 | CoverSet | [ ] |
| 5 | DashDodgeRollSet | [ ] |
| 6 | StairsSet | [ ] |
| 7 | PushSet | [ ] |
| 8 | PullSet | [ ] |
| 9 | LiftSet | [ ] |
| 10 | NarrowPassageSet | [ ] |
| 11 | ItemPickupSet | [ ] |
| 12 | ResourceGatheringSet | [ ] |
| 13 | StorageUnitsSet | [ ] |
| 14 | SurvivalSet | [ ] |
| 15 | DBNOSet | [ ] |

### 4.5 一括リターゲット（実証済み・推奨）

> **✅ 実証結果**: UE 5.5.4 で 1,250+ アニメーションを一度にリターゲットすることに成功しました。
> メモリ不足やクラッシュは発生せず、安定して動作しました。

```
[全アニメーションを一度にリターゲットする場合]

1. /Game/FreeAnimationLibrary/Animations/ を開く

2. フィルターを設定（任意）:
   - Content Browser 右上のフィルターアイコンをクリック
   - 「Animation Sequence」にチェック

3. Ctrl + A で全選択

4. 右クリック → 「Retarget Animations」
   ※「Retarget Animation Assets」ではない

5. ダイアログで設定:
   - Source Skeletal Mesh: SK_Mannequin（Mannequin_UE4 フォルダ内）
   - Target Skeletal Mesh: SKM_UEFN_Mannequin
   - Auto Generate Retargeter: オフ
   - Retarget Asset: RTG_FreeAnim_to_UEFN

6. 全アニメーションを選択 → 「Export Animations」

7. Export Path で出力先を選択
   - ☑ Use Source Path をオンにすると元のフォルダ構造が維持される

8. 処理完了を待つ（数分程度）

※ 処理中はエディタがやや重くなりますが、フリーズではありません。
```

#### 実証結果（2026-01-21）

| 項目 | 結果 |
|------|------|
| リターゲット数 | 1,250+ アニメーション |
| 処理時間 | 数分程度 |
| エラー | なし |
| クラッシュ | なし |
| 出力先 | 元のフォルダ構造を維持 |
| 命名規則 | 末尾に「1」が追加 |

---

## 5. Step 4: 検証

### 5.1 アニメーション再生確認

```
1. Content Browser でリターゲット済みアニメーションを開く
   パス: /Game/Characters/UEFN_Mannequin/Animations/Retargeted/

2. アニメーションをダブルクリックして Animation Editor を開く

3. 以下を確認:
   ✓ ポーズが正しい（手足の位置が自然）
   ✓ Root Motion が正しく適用されている
   ✓ 足が地面にめり込んでいない
   ✓ 手の位置が自然
   ✓ 回転が正しい（捻れていない）
```

### 5.2 優先確認アニメーション

| カテゴリ | アニメーション名 | 確認ポイント |
|---------|-----------------|-------------|
| Climbing | anim_Climb_Up | 壁登りポーズ、手足の配置 |
| Climbing | anim_Climb_Idle | 壁待機ポーズ |
| Climbing | anim_Climb_Move_* | 8方向移動 |
| LedgeClimb | anim_LedgeClimb_Idle | レッジ待機、手の位置 |
| LedgeClimb | AM_ClimbUp_At_Top | 登り上げモンタージュ |
| Walk | anim_Walk_Fwd_Loop | 歩行ループ、足の接地 |
| Jog | anim_Jog_Loop_Fwd | 走行ループ |

### 5.3 問題発生時の対処

| 症状 | 原因 | 対処法 |
|------|------|--------|
| ポーズが大きくずれる | チェーンマッピング不正 | Retargeter で Chain Mapping を確認・修正 |
| 足が地面にめり込む | Root 高さオフセット | Retargeter の Root Settings → Translation Offset (Z) を調整 |
| 腕が不自然な角度 | IK Weight 不適切 | Chain Settings で FK/IK Blend を調整（FK 寄りに） |
| 手首がねじれる | 回転軸の違い | Chain Settings で Rotation Mode を変更 |
| アニメーションが表示されない | スケルトン不一致 | Source/Target IK Rig のスケルトン設定を確認 |

### 5.4 検証チェックリスト

- [ ] クライミング系アニメーション（8方向移動）が正常再生
- [ ] レッジ系アニメーションが正常再生
- [ ] 歩行/走行アニメーションが正常再生
- [ ] Root Motion が正しく適用されている
- [ ] AM_ClimbUp_At_Top モンタージュが正常再生
- [ ] 手足の IK 位置が自然

---

## 6. トラブルシューティング

### 6.1 IK Rig 作成時の問題

#### 「+ Add」メニューに IK Rig がない

```
原因: Retargeting サブカテゴリを展開していない

対処:
1. Content Browser の「+ Add」をクリック
2. 「Animation」カテゴリを探してクリック（展開）
3. 「Retargeting」サブカテゴリをクリック（展開）
4. その中に「IK Rig」と「IK Retargeter」がある
```

#### Auto Retarget Chains が失敗する

```
原因: ボーン名がテンプレートと大きく異なる

対処:
1. 通知ウィンドウのエラーメッセージを確認
2. 手動でチェーンを作成（2.3 手動設定を参照）
3. 特に pelvis の Retarget Root 設定を忘れずに
```

### 6.2 Retargeter の問題

#### マッピングが自動で設定されない

```
原因: Source と Target のチェーン名が異なる

対処:
1. IK_FreeAnimationLibrary のチェーン名を確認
2. IK_UEFN_Mannequin のチェーン名を確認
3. 名前が異なる場合:
   - 手動でドロップダウンからマッピング
   - または IK Rig でチェーン名を変更
```

#### プレビューが表示されない

```
原因: Target IK Rig が設定されていない

対処:
1. Details パネルで Target IKRig Asset を確認
2. IK_UEFN_Mannequin が選択されているか確認
3. 設定されていなければ選択
```

### 6.3 リターゲット後の問題

#### 手足がねじれる

```
対処:
1. RTG_FreeAnim_to_UEFN を開く
2. Chain Mapping で該当チェーン（例: LeftArm）を選択
3. 右側の Settings パネルで:
   - FK Rotation Mode を「One to One」→「Interpolated」に変更
   - FK Rotation Weight を 0.8 程度に下げる
```

#### バッチリターゲットがクラッシュする

```
対処:
1. より小さい単位（10-20個ずつ）でリターゲット
2. エディタを再起動してメモリをクリア
3. Edit → Editor Preferences → Performance でメモリ設定を確認
4. 必要に応じて PC を再起動
```

---

## 7. 完了条件

### Exit Criteria

- [ ] `IK_FreeAnimationLibrary` が作成されている
- [ ] `RTG_FreeAnim_to_UEFN` が作成されている
- [ ] FreeAnimationLibrary の全アニメーション（133個）がリターゲット済み
- [ ] FreeSampleAnimationSet の全アニメーション（182個）がリターゲット済み
- [ ] 主要アニメーション（クライミング、レッジ、歩行）が正常再生確認済み
- [ ] リターゲット済みアニメーションが `/Game/Characters/UEFN_Mannequin/Animations/Retargeted/` に保存されている

---

## 8. 次のフェーズへ

Phase 2 が完了したら、Phase 3（AC_Climbing 改修）に進みます。

### Phase 3 で使用するリターゲット済みアニメーション

| 用途 | アニメーション | パス |
|------|--------------|------|
| 壁移動（8方向） | anim_Climb_Up, anim_Climb_Down, anim_Climb_Left, anim_Climb_Right 等 | `Retargeted/FreeAnimationLibrary/Climbing_Animations/Climbing/` |
| 壁待機 | anim_Climb_Idle | `Retargeted/FreeAnimationLibrary/Climbing_Animations/Idle/` |
| 壁遷移 | anim_Wall_Jump_Out, anim_GrabWall_From_Top | `Retargeted/FreeAnimationLibrary/Climbing_Animations/WallChange/`, `WallGrab_unGrab/` |
| 登り上げ | AM_ClimbUp_At_Top, anim_ClimbUp_At_Top | `Retargeted/FreeAnimationLibrary/Climbing_Animations/WallGrab_unGrab/` |
| レッジ | anim_LedgeClimb_* | `Retargeted/FreeAnimationLibrary/LedgeClimb/` |

---

## 付録: UE 5.5 IK リターゲットシステム クイックリファレンス

### IK Rig 作成方法（UE 5.5.4）

| 手順 | 操作 |
|------|------|
| 1 | Content Browser → 「+ Add」ボタン |
| 2 | Animation → **Retargeting** → IK Rig |
| 3 | スケルタルメッシュを選択 |
| 4 | Auto Retarget Chains でチェーン自動生成 |

### IK Retargeter 作成方法（UE 5.5.4）

| 手順 | 操作 |
|------|------|
| 1 | Content Browser → 「+ Add」ボタン |
| 2 | Animation → **Retargeting** → IK Retargeter |
| 3 | Source IK Rig を選択 |
| 4 | Target IK Rig を Details で設定 |

### バッチリターゲット方法（UE 5.5.4 実証済み）

> **⚠️ 重要**: UE 5.5.4 では、メニュー名が「Retarget Animation Assets」ではなく「**Retarget Animations**」です。

| 手順 | 操作 |
|------|------|
| 1 | アニメーションを選択（Ctrl+A で全選択可） |
| 2 | 右クリック → **「Retarget Animations」** |
| 3 | Source Skeletal Mesh: SK_Mannequin（FreeSampleAnimationSet/Demo/Mannequin_UE4/）を選択 |
| 4 | Target Skeletal Mesh: SKM_UEFN_Mannequin を選択 |
| 5 | Auto Generate Retargeter: **オフ** |
| 6 | Retarget Asset: RTG_FreeAnim_to_UEFN を選択 |
| 7 | Export Path: 出力先フォルダを選択（Use Source Path をオンで元のフォルダ構造を維持） |
| 8 | 「Export Animations」ボタンをクリック |

### リターゲット結果の確認方法

| 確認項目 | 方法 |
|---------|------|
| **サムネイル色** | オレンジ色 = リターゲット済み（UEFN_Mannequin）、白/青 = オリジナル |
| **ファイル名** | 末尾に「1」が追加される（例: A_JogBwd_Loop → A_JogBwd_Loop1） |
| **スケルトン確認** | アニメーションを開き、Skeleton が SK_UEFN_Mannequin であることを確認 |
| **プレビュー確認** | Animation Editor でオレンジ色のキャラクターが表示されれば成功 |

---

## 変更履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 1.0 | 2026-01-21 | 初版作成 |
| 2.0 | 2026-01-21 | UE 5.5.4 対応版に更新（IK Rig作成手順、Auto Retarget Chains追加） |
| 2.1 | 2026-01-21 | ファイルパス修正: FreeAnimationLibrary/Climbing_Animations のサブフォルダ構造（Climbing/, Idle/, WallChange/, WallGrab_unGrab/）を反映、FreeSampleAnimationSet のネスト構造（Mannequin/RootMotion/等）を修正 |
| 2.2 | 2026-01-21 | メニュー階層修正: UE 5.5.4 では IK Rig / IK Retargeter は「Animation → **Retargeting**」サブカテゴリ内に配置されていることを反映 |
| 2.3 | 2026-01-21 | SK_Mannequin パス修正: FreeAnimationLibrary のアニメーションが実際に参照しているスケルトンは `/Game/FreeSampleAnimationSet/Demo/Mannequin_UE4/Meshes/SK_Mannequin`（UE4スケルトン）であることを反映。既存の IK_FreeAnimationLibrary（`/Game/FreeAnimationLibrary/Animations/Rigs/`）を使用する旨を追記 |
| **3.0** | **2026-01-21** | **UE 5.5.4 実証結果を反映（Phase 2 完了）：** |
| | | - **バッチリターゲットのメニュー名**: 「Retarget Animation Assets」→「**Retarget Animations**」に修正 |
| | | - **Retarget Animations ダイアログ**: Source/Target Skeletal Mesh、Auto Generate Retargeter オフ、Retarget Asset の設定手順を追加 |
| | | - **Use Source Path オプション**: 元のフォルダ構造を維持する設定方法を追加 |
| | | - **命名規則**: リターゲット済みアニメーションはファイル名末尾に「1」が追加されることを明記 |
| | | - **サムネイル識別方法**: オレンジ色 = リターゲット済み（UEFN_Mannequin）、白/青 = オリジナルを追加 |
| | | - **実証結果**: 1,250+ アニメーションの一括リターゲットに成功、処理時間・エラー・クラッシュ状況を記録 |
| | | - **クイックリファレンス**: バッチリターゲット方法を実証済みの手順に更新 |

---

**End of Document**
