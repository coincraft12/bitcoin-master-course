# 1부 미니 과제: 내 노드로 만든 탐색기 리포트

2-4 · PART 1 MINI PROJECT. 1부에서 배운 내용이 모두 들어가는 과제입니다.

## 과제

| 단계 | 할 일 |
|---|---|
| 1 | regtest에서 alice → bob 송금 3건을 서로 다른 금액으로 보내고 블록 생성 |
| 2 | `lib/rpc.py`로 최근 블록 목록, 각 송금 트랜잭션의 입력 수·출력 수, 출력 중 잔돈으로 보이는 것을 출력 |
| 3 | alice의 UTXO 목록 합계가 `getbalance`와 일치함을 출력으로 보이기 (1-4) |
| 4 | 수수료를 계산해 출력하기. 힌트: `getblock` verbosity 3이나 이전 트랜잭션 조회 (5-1 예습, 부분 점수) |

**제출물:** `lib/rpc.py`를 쓴 스크립트와 실행 결과.

조건
- 금액 계산은 sat 정수로 합니다(2-4). `btc_to_sat`, `sat_to_btc`를 쓰세요. float 금지.
- 2단계의 잔돈 판정 기준은 스스로 세우고, 그 기준을 제출물에 한두 줄로 적습니다.
- 4단계는 5강에서 다시 다루므로 부분 점수를 줍니다.

## 파일

| 파일 | 내용 |
|---|---|
| `exercise_explorer_report.py` | 과제용 뼈대. 함수 여섯 개(`recent_blocks`, `find_payments`, `guess_change`, `fee_sat`, `feerate`, `utxo_vs_balance`)를 구현하면 리포트가 완성된다 |
| `solution/make_payments.sh` | 정답 1단계: alice → bob 0.1, 0.25, 0.7 BTC 송금 후 블록 1개 생성 |
| `solution/explorer_report.py` | 정답 2~4단계 리포트 |

## 진행

```bash
env/setup_regtest.sh                                           # 표준 환경 (아직 안 했다면)
part1/lesson-08/assignment/solution/make_payments.sh           # 1단계 (직접 bitcoin-cli로 해도 된다)
python part1/lesson-08/assignment/exercise_explorer_report.py  # 내 풀이 실행
python part1/lesson-08/assignment/solution/explorer_report.py  # 정답과 비교
```

1단계를 직접 한다면:

```bash
CLI="bitcoin-cli -regtest"
$CLI -rpcwallet=alice sendtoaddress "$($CLI -rpcwallet=bob getnewaddress)" 0.1
$CLI -rpcwallet=alice sendtoaddress "$($CLI -rpcwallet=bob getnewaddress)" 0.25
$CLI -rpcwallet=alice sendtoaddress "$($CLI -rpcwallet=bob getnewaddress)" 0.7
$CLI -rpcwallet=miner -generate 1
```

## 정답 풀이의 기준

- **송금 찾기**: alice 지갑의 `listtransactions`에서 `category`가 `send`이고 받는 주소가 bob 지갑 소유(`bob.getaddressinfo(주소)["ismine"]`)인 항목. 블록에 담긴 것 중 최근 3건.
- **입력·출력 수**: `getblock(블록해시, 3)`에서 그 트랜잭션의 `vin`, `vout` 길이.
- **잔돈 추정(둥근 금액 휴리스틱)**: 사람이 정하는 지급액은 0.1 BTC처럼 끝자리가 0으로 끝나기 쉽고, 잔돈은 "입력 − 지급 − 수수료"라 끝자리가 지저분합니다. sat 금액의 끝자리 0이 가장 적은 출력이 하나뿐이면 그것을 잔돈으로 봅니다. 정답 스크립트는 추정 결과를 alice 지갑의 `getaddressinfo`로 확인해 맞았는지도 보여 줍니다. 지갑 없이 남의 트랜잭션을 볼 때는 이런 휴리스틱밖에 없고, 틀릴 수 있다는 점이 프라이버시(14-3)와 이어집니다.
- **UTXO 합 = 잔액**: `listunspent(0)`에서 `safe`가 참인 출력의 합(sat)과 `getbalance`(sat)를 비교. `listunspent` 기본값(1 확인 이상)만 쓰면 방금 만든 미확정 잔돈이 빠져 어긋날 수 있습니다.
- **수수료**: 입력이 쓴 이전 출력 금액의 합 − 출력 금액의 합. verbosity 3에서는 각 `vin`에 `prevout`(금액·스크립트)이 붙어 있어 한 번에 계산됩니다. `prevout`이 없으면 `getrawtransaction(이전 txid, True)`로 이전 출력 금액을 조회합니다. 계산값을 노드가 주는 `fee` 필드와도 대조합니다. 수수료율은 수수료 ÷ vsize (sat/vB).

## 기대 출력 (정답)

표준 환경 직후 `make_payments.sh`를 한 번 실행한 뒤의 예입니다. txid, 주소, 해시, size, weight, 출력 순서는 실행마다 다릅니다. 잔돈 출력의 위치(0번인지 1번인지)는 지갑이 무작위로 정합니다.

```
== [2단계] 최근 블록 ==
height  nTx    size   weight  hash
    94    1     250      892  48681e9efa5dc548…
    95    1     250      892  4a7414980c3baf23…
    96    1     250      892  3a9b3d76ceca3bb0…
    97    1     250      892  13fecdeb0692079e…
    98    1     250      892  cea8471f82ea49f1…
    99    1     250      892  750b85a42b308db8…
   100    1     250      892  8e81023f9bb54b49…
   101    1     250      892  658394d2abafc04b…
   102    3     698     2024  1ded3b1e2b5db009…
   103    4     920     2575  cf1238aa4d756ee2…

== [2·4단계] alice → bob 송금 3건: 입출력, 잔돈 추정, 수수료 ==
[1] c9092aec23dc0e6d76b526490bc1c935bf2ff51af771c07757e460d01f3aa24b  (블록 103)
    입력 1개, 출력 2개
    출력 0:    10000000 sat  bcrt1qk22v2ucuf0d4p5sslwxpc3x4ct23de6uafecev
    출력 1:   489997180 sat  bcrt1qhy8uq2dm8kgp67umwzwsnehgy7k634xjsyz2ud  ← 잔돈 추정
    잔돈 추정: 출력 1 (끝자리 0이 가장 적은 금액) / 지갑 확인: alice 소유 → 맞음
    수수료: 2820 sat (vsize 141, 20.00 sat/vB) · 노드 fee 필드와 일치
[2] 3a814e2f77e382f76bc0f667ef503c26b4996e20714405269c49f43710acf743  (블록 103)
    입력 1개, 출력 2개
    출력 0:   464994360 sat  bcrt1qesc7ftsguwkfkjunsfuxv42gs8stwt2l82xdcu  ← 잔돈 추정
    출력 1:    25000000 sat  bcrt1q8cs4gw0ez2wkd7plrwwp7yr54v3yxj6cs84arz
    잔돈 추정: 출력 0 (끝자리 0이 가장 적은 금액) / 지갑 확인: alice 소유 → 맞음
    수수료: 2820 sat (vsize 141, 20.00 sat/vB) · 노드 fee 필드와 일치
[3] af58a55ccc4618c77a47851b7f9e7ddf35e3cbda8121d4f8574c75600307fcad  (블록 103)
    입력 1개, 출력 2개
    출력 0:    70000000 sat  bcrt1qmrvc6h2n5kkrh4u58eurret8dqnd7u8crvphvj
    출력 1:   394991540 sat  bcrt1qk929r27u4326k27tqcdxh0jjzm3xd6l22v5mf2  ← 잔돈 추정
    잔돈 추정: 출력 1 (끝자리 0이 가장 적은 금액) / 지갑 확인: alice 소유 → 맞음
    수수료: 2820 sat (vsize 141, 20.00 sat/vB) · 노드 fee 필드와 일치
    수수료 합계: 8460 sat = 0.00008460 BTC

== [3단계] alice의 UTXO 합계 vs getbalance ==
UTXO 1개 합계: 394991540 sat = 3.94991540 BTC
getbalance      : 394991540 sat = 3.94991540 BTC
일치
```

(txid·주소·해시·size·weight·출력 순서는 실행마다 다름)

읽는 법
- 블록 103의 nTx가 4인 것은 코인베이스 + 송금 3건이기 때문입니다.
- 둘째·셋째 송금의 입력은 앞 송금의 잔돈입니다. 지갑은 확인되지 않은 자기 잔돈도 쓸 수 있습니다. 그래서 세 송금이 사슬처럼 이어지고, 마지막 잔돈 하나만 alice의 UTXO로 남습니다.
- 수수료율 20 sat/vB는 `bitcoin.conf`의 `fallbackfee=0.0002`(BTC/kvB)입니다. P2WPKH 입력 1개·출력 2개 트랜잭션은 141 vB이므로 141 × 20 = 2820 sat. 지갑 주소 유형이 다르면 vsize와 수수료도 다릅니다.

## 흔히 막히는 지점

- **"블록에 담긴 alice → bob 송금이 없습니다".** 송금 후 블록을 만들지 않았습니다. `bitcoin-cli -regtest -rpcwallet=miner -generate 1`.
- **UTXO 합계와 getbalance가 다름.** `listunspent()`는 기본으로 1 확인 이상만 돌려줍니다. 블록을 만들거나 `listunspent(0)`을 쓰고, 남이 보낸 미확정 출력(`safe`가 거짓)은 빼세요.
- **수수료가 이상하게 큼.** BTC 금액을 float로 더했거나, 코인베이스(`vin`에 `coinbase`)를 계산에 넣었습니다. 코인베이스에는 이전 출력이 없습니다.
- **`KeyError: 'prevout'`.** `getblock`에 verbosity 3을 주지 않았습니다.
- **`ModuleNotFoundError: No module named 'lib'`.** 저장소 최상위에서 파일 경로로 실행하세요.
