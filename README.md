# DiffServ 網路模擬器 (DiffServ Network Simulation)

這是一個基於 Python 的 Differentiated Services (DiffServ) 網路架構模擬程式。此專案模擬了封包從來源端 (Source) 經過邊緣節點 (Edge Node) 和核心節點 (Core Node) 到達目的地的過程，並實作了不同服務等級的流量控制與排程機制。

## 功能特點

本模擬器支援三種 DiffServ 服務等級，優先級由高至低分別為：
*   **EF (Expedited Forwarding)**: 最高優先級，模擬低延遲需求的流量。
*   **AF (Assured Forwarding)**: 中等優先級，但在流量超標時可能會被重新標記 (Remarking) 降級。
*   **BE (Best Effort)**: 最低優先級，像是傳統的網際網路流量。

### 核心機制
*   **來源端 (Source)**: 根據輸入模式產生封包。
*   **邊緣節點 (Edge Node)**: 執行流量監管 (Traffic Policing)。
    *   **Remarking**: 預設策略會將每 5 個 AF 封包中的第 1 個降級為 BE (可於設定中調整)。
*   **核心節點 (Core Node)**: 執行優先權佇列 (Priority Queuing)。
    *   擁有三個獨立佇列 (EF, AF, BE)。
    *   採用絕對優先權調度 (Strict Priority Scheduling)，只要高優先權佇列有封包，就會先傳送。
    *   佇列容量限制 (預設各為 1 個封包，可調整)，若佇列滿則會丟包。

## 系統需求

*   Python 3.x
*   無須安裝額外第三方套件 (僅使用標準函式庫)。

## 使用方式

請在專案根目錄下執行 `main.py` 並使用 `--patterns` (或 `-p`) 參數指定每個來源的流量類型。

### 參數說明
*   `E`: Expedited Forwarding (EF)
*   `A`: Assured Forwarding (AF)
*   `B`: Best Effort (BE)

### 執行範例

**範例 1：單一混合流量**
模擬 5 個來源，分別為 EF, AF, BE, AF, EF。
```bash
python main.py --patterns E A B A E
```
或者連在一起寫：
```bash
python main.py --patterns EABAE
```

**範例 2：多個參數輸入**
```bash
python main.py -p E A B
```

## 模擬結果與輸出

程式執行時會顯示詳細的封包流動日誌：
*   `[Edge Receive]`: 邊緣節點接收封包
*   `[Edge Send]`: 邊緣節點發送封包 (可能已發生 Remarking)
*   `[Core Receive]`: 核心節點接收封包 (進入佇列)
*   `[Core Send]`: 核心節點發送封包 (可能因佇列滿而遺失)
*   `[Dst Reach]`: 封包抵達目的地

模擬結束後會顯示統計表格：
*   **Completion Time**: 來源端完成所有封包傳輸的時間。
*   **Drop Rate (%)**: 封包遺失率。
*   **Avg Latency**: 平均延遲時間 (ms)。

## 參數設定

您可以在 `src/config.py` 中調整所有模擬參數，包括：
*   **Time Parameters**: 模擬時間步長、封包產生間隔。
*   **Network Delay**: 各節點間的傳輸與傳播延遲、處理時間。
*   **Queue Capacity**: 核心節點各佇列的容量 (`CORE_QUEUE_CAPACITY_EF` 等)。
*   **Traffic Policing**: AF 封包的降級策略 (`AF_REMARKING_INTERVAL`)。
*   **Simulation Target**: 每個來源需成功傳送的封包數量。

## 網頁介面 (Web Interface)

本專案包含一個現代化的 React 網頁介面，提供圖形化儀表板來執行模擬與分析結果。

### 啟動方式

1.  **啟動後端伺服器**:
    ```bash
    pip install -r requirements.txt
    python server.py
    ```

2.  **啟動前端網頁**:
    ```bash
    cd web
    npm install
    npm install axios chart.js react-chartjs-2
    npm run dev
    ```

3.  開啟瀏覽器訪問顯示的網址 (例如 `http://localhost:5173`)。
