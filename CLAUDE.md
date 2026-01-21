# AthleticTrial

 - **Ultra Think**
 - **返答は日本語**
 - **適時、作業内容と進捗状況を更新し、knowledge-graph を使用して プロジェクト名 エンティティ と関連付けて保存も行う**


## プロジェクト概要

このプロジェクトは、**Windows 11** 上の **Unreal Engine 5.5.4** で **[Game Animation Sample](https://www.fab.com/ja/listings/880e319a-a59e-4ed2-b268-b32dac7fa016)** をベースにして、 既存のAnimationTestProject  @C:\Users\work0\uechi\UEProjects\AnimationTestProject のプレイヤーキャラクターの挙動を移行し、アクションゲームを作成するプロジェクトである。


## 環境

- **OS**: Windows 11
- **Unreal Engine バージョン**: **UE 5.5.4**
- **ベースプロジェクト**: [Game Animation Sample](https://www.fab.com/ja/listings/880e319a-a59e-4ed2-b268-b32dac7fa016)
- **knowledge-graph を使用して適時作業内容と進捗状況を更新**

## プロジェクト構成

### コンテンツフォルダ

- **Characters/** - キャラクターアセット
- **FreeAnimationLibrary/** - 無料アニメーションライブラリ（外部アセット） [FreeAnimationLibrary](https://www.fab.com/ja/listings/481ef75b-892b-424f-a213-f1cc058c9c19)
- **ThirdPerson/** - サードパーソンテンプレート関連
  - Maps/ - レベルマップ
  - Blueprints/ - ゲームモード、キャラクターBP等
- **StarterContent/** - UE標準のスターターコンテンツ
- **LevelPrototyping/** - レベルプロトタイピング用アセット

## レンダリング設定

- **Graphics API**: DirectX 12
- **Shader Model**: SM6
- **Ray Tracing**: 有効
- **Global Illumination**: Lumen
- **Shadow**: Virtual Shadow Maps

## 有効なプラグイン

- **ModelingToolsEditorMode** (エディタ専用)

## プロジェクトの目的

このプロジェクトは、**Windows 11** 上の **Unreal Engine 5.5.4** で **[Game Animation Sample](https://www.fab.com/ja/listings/880e319a-a59e-4ed2-b268-b32dac7fa016)** をベースにして、 既存のプロジェクト @C:\Users\work0\uechi\UEProjects\AnimationTestProject のプレイヤーキャラクターの挙動を移行し、アクションゲームを作成するプロジェクトである。

---

## Claude Code で利用可能な Model Context Protocol (MCP) サーバ

### MCP サーバとは

MCP（Model Context Protocol）サーバは、Claude Code が外部ツール、API、データソースにアクセスするための統合機能です。データベースのクエリ、モニタリングデータの分析、GitHub ワークフローの管理、各種統合の自動化などが可能になります。

### このプロジェクトで利用可能な MCP サーバ

現在、このプロジェクトには以下の MCP サーバが構成されています：

#### 1. **knowledge-graph**
- **機能**: 高度なナレッジグラフ管理（プロジェクト分離・タグ・検索機能付き）
- **使い所**: プロジェクト固有の知識ベース構築、作業進捗の永続化、セッション間での文脈継承
- **データ保存先**: `.knowledge-graph/memory.db` (SQLite)
- **主な操作**:
  - **search_knowledge**: エンティティをテキストまたはタグで検索（完全一致/あいまい検索対応）
  - **create_entities**: 新規エンティティの作成（名前、タイプ、観測、タグ付き）
  - **add_observations**: 既存エンティティへの観測（事実）の追加
  - **create_relations**: エンティティ間の関係性の作成
  - **delete_entities**: エンティティと関連する関係性の削除
  - **delete_observations**: 特定の観測の削除
  - **delete_relations**: 特定の関係性の削除
  - **read_graph**: プロジェクト全体のナレッジグラフを取得
  - **open_nodes**: 特定のエンティティを名前で取得
  - **add_tags**: エンティティへのタグ追加
  - **remove_tags**: エンティティからのタグ削除

##### エンティティタイプ
| タイプ | 用途 | 例 |
|--------|------|-----|
| `person` | 人物 | 開発者、クライアント |
| `technology` | 技術・ツール | UE5, Blueprint, Motion Matching |
| `project` | プロジェクト | AnimationTestProject, AthleticTrial |
| `company` | 企業・組織 | Epic Games |
| `concept` | 概念・アイデア | リターゲット、IK Rig |
| `event` | イベント・マイルストーン | 統合作業開始、フェーズ1完了 |
| `preference` | 設定・好み | コーディング規約 |

##### 使用例
```
# エンティティの検索
search_knowledge(query="AnimationTestProject", project_id="AnimationTestProject")

# エンティティの作成
create_entities(
  entities=[{
    "name": "AC_Climbing",
    "entityType": "technology",
    "observations": ["壁登りシステムを実装するActorComponent", "E_ClimbStateを使用"],
    "tags": ["blueprint", "climbing", "component"]
  }],
  project_id="AnimationTestProject"
)

# 関係性の作成
create_relations(
  relations=[{
    "from": "AC_Climbing",
    "to": "BP_ThirdPersonCharacter",
    "relationType": "attached_to"
  }],
  project_id="AnimationTestProject"
)

# 観測の追加
add_observations(
  observations=[{
    "entityName": "AnimationTestProject",
    "observations": ["フェーズ1: リターゲット設定完了"]
  }],
  project_id="AnimationTestProject"
)
```

##### このプロジェクトでの活用方針
- **project_id**: `AthleticTrial` を使用
- **作業進捗**: 各作業の開始・完了を `event` タイプで記録
- **技術情報**: Blueprint、アニメーション、リグ等を `technology` タイプで記録
- **関係性**: プロジェクト間の統合関係、アセット間の依存関係を記録

#### 2. **deepwiki**
- **機能**: GitHub リポジトリのドキュメント取得・検索
- **使い所**: リポジトリの構造理解、ドキュメント参照、技術的な質問への回答
- **主な操作**: Wiki構造の取得、コンテンツ閲覧、質問応答

#### 3. **context7**
- **機能**: 最新のライブラリドキュメントとコード例の取得
- **使い所**: ライブラリのAPI仕様確認、使用方法の学習
- **主な操作**: ライブラリID解決、ドキュメント取得（code/infoモード）

#### 4. **github**
- **機能**: GitHub リポジトリの包括的な操作
- **使い所**: PR作成・レビュー、Issue管理、ファイル操作、ブランチ管理
- **主な操作**:
  - リポジトリ検索・作成
  - ファイルの取得・作成・更新
  - Issue/PR の作成・管理
  - レビューの投稿、マージ操作

#### 5. **filesystem**
- **機能**: ローカルファイルシステムへのアクセス
- **使い所**: ファイル・ディレクトリの読み書き、検索、メタデータ取得
- **主な操作**:
  - ファイルの読み取り・書き込み・編集
  - ディレクトリ操作
  - ファイル検索・ツリー表示

#### 6. **windows-mcp**
- **機能**: Windows デスクトップの直接操作
- **使い所**: アプリケーション起動、UI操作、システム制御
- **主な操作**:
  - アプリケーション起動・ウィンドウ切り替え
  - マウス・キーボード操作（クリック、入力、スクロール）
  - デスクトップ状態のキャプチャ
  - PowerShellコマンド実行
  - Webスクレイピング

#### 7. **brave-search**
- **機能**: Brave Search API を使用した Web 検索
- **使い所**: 最新情報の検索、Web コンテンツの収集、ローカルビジネス検索
- **主な操作**: Web検索、ローカル検索（位置情報ベース）

#### 8. **unreal-handshake**
- **機能**: Unreal Engine エディタとの高度な連携
- **使い所**: Blueprint操作、アセット管理、レベル編集、UI作成
- **主な操作**:
  - Blueprint の作成・編集・ノード追加
  - コンポーネント・変数の追加
  - アクターのスポーン・操作
  - フォリッジ配置
  - マテリアル作成・適用
  - UMG Widget の作成・編集
  - プロジェクト構造の管理

#### 9. **unrealMCP**
- **機能**: Unreal Engine の基本的な操作
- **使い所**: アクター管理、Blueprint基本操作、物理設定
- **主な操作**:
  - レベル内のアクター取得・操作
  - Blueprint の作成・コンパイル
  - コンポーネントの追加・設定
  - 物理プロパティの設定
  - UMG Widget の基本操作

### MCPサーバー優先順位

| サーバー | 役割 | 制御 | 主要ユースケース |
|----------|------|------|------------------|
| knowledge-graph | ナレッジグラフ管理 | 読み書き | 作業進捗記録、プロジェクト知識の永続化 |
| ddg-search | Web検索 | 読取専用 | 最新情報検索 |
| context7 | 技術文書検索 | 読取専用 | API/ライブラリドキュメント |
| deepwiki | コードベース分析 | 読取専用 | アーキテクチャ理解 |
| github | GitHub API | 読み書き | Issue/PR管理 |
| git | バージョン管理 | 読み書き | コミット・ブランチ管理 |
| unreal-handshake | Unreal Engine エディタとの高度な連携 | 読み書き | Blueprint操作、アセット管理、レベル編集、UI作成 |
| blender-mcp | 3D制作 | 読み書き | 3Dアセット生成 |

