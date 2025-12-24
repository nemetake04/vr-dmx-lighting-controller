# vr-dmx-lighting-controller
VRコントローラ（Meta Quest / Oculus）からの入力を用いて、   DMX照明をリアルタイムに制御するシステムです。  Unityで取得したスティック・ボタン入力をUDPでPCへ送信し、   PythonでDMX信号に変換して照明機材を制御します。

## 🎯 Features（特徴）

### DMX制御
- Python から DMX 機器を直接制御
- USB–RS485（DMX Control / RS485 アダプタ）を使用
- COMポート経由で DMX パケットを送信

### UI / インタラクション
- 直感的操作による照明制御
- デモルームでの体験型インスタレーションを想定

### 拡張性
- ライブ・展示用途を想定した拡張可能な構成
- MAX / Python / Arduino 間の連携設計

---

## 🛠 使用技術・環境（Tech Stack）

### ハードウェア
- DMX対応照明機器  
  - STAGE EVOLUTION MINI SPOT 30  

### ソフトウェア
- Python
- MAX/MSP
- USB–RS485（DMX512）

---

## 📁 ディレクトリ構成（Directory Structure）

dmx-lighting-control/  
├─ README.md  
├─ python/     
│ └─ VR-DMX.py/  
└─ Unity/  
└─ Unity_controller.cs/  


---

## 🧠 設計のポイント（Design Concept）

- ステックには絶対値制御ではなく **変化量（delta）制御**を採用
- 微小入力を無視するデッドゾーン処理による安定化
- DMX値のクランプ処理による暴走防止

---

## 🎨 想定用途（Use Case）

- ライブ演出
- メディアアート展示
- 体験型インスタレーション
- インタラクティブ照明作品
