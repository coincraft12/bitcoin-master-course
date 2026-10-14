# lesson-08 · 2-4 Python으로 노드 제어: RPC 래퍼, Decimal, 1부 미니 과제

1부 기초 · 2강 Bitcoin Core 실습 환경

## 목표

- Python으로 JSON-RPC 래퍼를 작성하고 호출할 수 있다
- 금액을 Decimal로 다뤄야 하는 이유를 설명할 수 있다
- 실습 저장소 구조와 lib 폴더가 자라는 방식을 이해한다

## lib/rpc.py

[lib/rpc.py](../../lib/rpc.py)가 이 차시에서 만드는 래퍼입니다. 과정 내내 자라는 lib 폴더의 첫 파일입니다.

| 부분 | 하는 일 |
|---|---|
| `PORTS` | 네트워크별 RPC 포트: main 8332, testnet4 48332, signet 38332, regtest 18443 |
| `RPC.__init__` | 쿠키 파일(2-3)을 읽어 인증 정보를 만들고, `wallet`을 주면 URL 끝에 `/wallet/<이름>`을 붙인다 |
| `__getattr__` | `rpc.getblock(h, 2)`처럼 RPC 이름이 곧 메서드 |
| `parse_float=Decimal` | 금액을 부동소수점으로 받지 않는다 |
| `body["error"]` | HTTP가 실패여도 본문에 오류가 있다. 상태 코드보다 본문을 먼저 읽는다 |

저장소 버전은 슬라이드 코드에 세 가지를 보탰습니다.

- `datadir` 기본값이 `BITCOIN_DATADIR` 환경변수를 먼저 읽습니다(macOS 등, [env/README.md](../../env/README.md)).
- 쿠키 파일이 없으면 원인을 알려 주는 오류 메시지를 냅니다.
- 금액 변환 헬퍼 `btc_to_sat`(Decimal BTC → sat 정수, float는 거부)과 `sat_to_btc`.

### 금액은 Decimal로 받고, sat 정수로 계산한다

```python
>>> 0.1 + 0.2
0.30000000000000004
```

```python
btc = alice.getbalance()
sat = int(btc * 100_000_000)
```

작은 오차가 쌓이면 잔돈·수수료 사고로 이어집니다(5-3). 내부 계산은 항상 sat 정수로 합니다(5-1).

## 실습: 최근 블록 리포트

준비: [env/README.md](../../env/README.md)의 표준 환경, `pip install requests`.

파일: `part1/lesson-08/recent_blocks.py` (슬라이드 코드 + 저장소 루트를 `sys.path`에 넣는 줄)

```python
# part1/lesson-08/recent_blocks.py
from lib.rpc import RPC
rpc = RPC()
tip = rpc.getblockcount()
print(f"{'height':>6} {'nTx':>4} {'size':>7} {'weight':>8}  hash")
for h in range(max(0, tip - 9), tip + 1):
    b = rpc.getblock(rpc.getblockhash(h), 1)
    print(f"{b['height']:>6} {b['nTx']:>4} {b['size']:>7} {b['weight']:>8}  {b['hash'][:16]}…")
alice = RPC(wallet="alice")
print("alice:", alice.getbalance(), "BTC =", int(alice.getbalance() * 100_000_000), "sat")
```

저장소 최상위에서 실행합니다.

```bash
python part1/lesson-08/recent_blocks.py
```

## 기대 출력

새 표준 환경(높이 102) 직후의 예입니다. 해시, size, weight는 실행마다 다릅니다.

```
height  nTx    size   weight  hash
    93    1     250      892  20803d609259ab90…
    94    1     250      892  48681e9efa5dc548…
    95    1     250      892  4a7414980c3baf23…
    96    1     250      892  3a9b3d76ceca3bb0…
    97    1     250      892  13fecdeb0692079e…
    98    1     250      892  cea8471f82ea49f1…
    99    1     250      892  750b85a42b308db8…
   100    1     250      892  8e81023f9bb54b49…
   101    1     250      892  658394d2abafc04b…
   102    3     698     2024  1ded3b1e2b5db009…
alice: 5.00000000 BTC = 500000000 sat
```

(해시·size·weight는 실행마다 다름)

- 블록 대부분은 nTx가 1입니다. regtest에서는 아무도 송금하지 않은 블록에 코인베이스만 담기기 때문입니다.
- 높이 102만 nTx가 3입니다. 2-2의 setup 스크립트에서 miner가 alice와 bob에게 보낸 송금 2건이 그 블록에만 담겼기 때문입니다.
- alice 잔액은 Decimal(`5.00000000`)로 출력되고, sat로 바꾼 값은 정수입니다.

## 흔히 막히는 지점

- **`ModuleNotFoundError: No module named 'lib'`.** 저장소 최상위가 아닌 곳에서 실행했습니다. 이 저장소의 스크립트는 맨 위의 `sys.path` 줄로 저장소 루트를 찾으므로 `python part1/lesson-08/recent_blocks.py`처럼 파일 경로로 실행하세요. 슬라이드 코드를 다른 곳에 옮겨 쓸 때는 그 줄도 함께 옮겨야 합니다.
- **`RuntimeError: 쿠키 파일이 없습니다`.** 노드가 꺼져 있거나(`bitcoind -regtest -daemon`), datadir이 다릅니다. macOS는 `export BITCOIN_DATADIR="$HOME/Library/Application Support/Bitcoin"`.
- **`ModuleNotFoundError: No module named 'requests'`.** `pip install requests`.
- **`RuntimeError: getbalance: {'code': -18, ...}`.** alice 지갑이 로드되지 않았습니다. `env/setup_regtest.sh`를 실행하세요.

## 1부 미니 과제

[assignment/README.md](assignment/README.md) — 내 노드로 만든 탐색기 리포트

## 퀴즈

[quiz/lesson-08.md](../../quiz/lesson-08.md)
