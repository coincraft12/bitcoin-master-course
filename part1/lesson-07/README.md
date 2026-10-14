# lesson-07 · 2-3 bitcoin-cli와 RPC: JSON-RPC 구조, 조회 연쇄, RPC 보안

1부 기초 · 2강 Bitcoin Core 실습 환경

## 목표

- bitcoin-cli가 JSON-RPC 클라이언트임을 설명할 수 있다
- 체인 → 블록 → 트랜잭션 순으로 조회를 이어갈 수 있다
- RPC 포트를 외부에 노출하면 안 되는 이유를 말할 수 있다

## 핵심 정리

- `bitcoin-cli`는 명령을 JSON으로 포장해 HTTP POST로 bitcoind의 RPC 포트(regtest 18443)에 보낼 뿐입니다. 같은 일을 curl, Python, 어떤 언어로든 할 수 있습니다.
- 인증: 기본은 **쿠키**(실행할 때마다 데이터 폴더에 `.cookie` 생성, 같은 컴퓨터의 cli가 읽어 인증). 원격·다중 사용자용은 **rpcauth**(비밀번호 해시만 설정 파일에 저장).
- 조회 연쇄(Core 31.1 기준): `getblockchaininfo` → `getblockhash <높이>` → `getblock <해시> 1` → `getrawtransaction <txid> true` → (hex만 있으면) `decoderawtransaction`. Core 31부터 `getblock`은 verbosity 1 이상에서 `coinbase_tx` 필드를 함께 줍니다. 막히면 `help <명령>`.
- `getblock` verbosity: 0 블록 전체 hex / 1 헤더 정보 + txid 목록(기본값) / 2 각 트랜잭션 상세 / 3 = 2 + 각 입력이 쓴 이전 출력 정보(금액·스크립트). 수수료 계산에는 3이 필요합니다(5-1).
- 노드 RPC(`getblockchaininfo`, `getblock`, `getrawtransaction`)와 지갑 RPC(`getbalance`, `sendtoaddress`, `listunspent`). 지갑이 여러 개 로드되어 있으면 `-rpcwallet=alice`로 지정하고, HTTP로는 `POST /wallet/alice`가 됩니다.
- **RPC는 지갑에서 돈을 보낼 수 있는 권한입니다.** rpcbind로 외부에 열지 말고, 원격 접근은 SSH 터널이나 VPN으로 합니다(12-1).

## 실습: 블록에서 트랜잭션까지

준비: [env/README.md](../../env/README.md)의 표준 환경(`env/setup_regtest.sh`), `jq`, `curl`.

### 슬라이드 명령

```bash
CLI="bitcoin-cli -regtest"
$CLI getblockchaininfo | jq '{chain, blocks, bestblockhash}'
HASH=$($CLI getblockhash $($CLI getblockcount))
$CLI getblock $HASH 1 | jq '{height, time, nTx, size, weight, tx}'
TXID=$($CLI getblock $HASH 1 | jq -r '.tx[0]')
$CLI getrawtransaction $TXID true | jq '{txid, vin, vout}'   # vin에 coinbase
# curl로 같은 RPC 직접 호출 → result, error, id 확인
COOKIE=$(cat ~/.bitcoin/regtest/.cookie)
curl -s --user "$COOKIE" -H 'content-type: text/plain;' http://127.0.0.1:18443/ \
  --data-binary '{"jsonrpc":"1.0","id":"cc","method":"getblockcount","params":[]}'
```

`lab.sh`에서는 쿠키 경로를 `${BITCOIN_DATADIR:-$HOME/.bitcoin}/regtest/.cookie`로 바꿔 macOS에서도 쓸 수 있게 했습니다.

### 과제(나레이션)

1. 2-2에서 alice와 bob에게 보낸 송금이 어느 블록에 있는지 찾는다.
2. `getblock`의 verbosity를 0, 1, 2로 바꿔 출력 크기를 비교한다.
3. 존재하지 않는 메서드 이름으로 curl을 보내 `error` 필드가 채워지는 것을 본다.

슬라이드 명령과 과제를 한 번에:

```bash
part1/lesson-07/lab.sh
```

## 기대 출력

새 표준 환경(높이 102) 직후의 예입니다. 해시, txid, 시간, 크기는 실행마다 다릅니다.

```
{
  "chain": "regtest",
  "blocks": 102,
  "bestblockhash": "1ded3b1e2b5db009d9bc51a47aced0ef8223364c14f6b09e17e0210e8653135c"
}
{
  "height": 102,
  "time": 1792051200,
  "nTx": 3,
  "size": 698,
  "weight": 2024,
  "tx": [
    "ca8004987c8911e01b79c14b79923016bd0d344548268c6e479befe8adb7b1b9",
    "77a1a82ba10a33c3611222680d56ffda7c9df9494fe3ca07069e44f337c712f9",
    "bed0f1f16a393be66c9dc2f2286efd831481109f2b1dfe9106f834041d5011da"
  ]
}
{
  "txid": "ca8004987c8911e01b79c14b79923016bd0d344548268c6e479befe8adb7b1b9",
  "vin": [
    {
      "coinbase": "016600",
      ...
    }
  ],
  "vout": [ ... ]
}
{"result":102,"error":null,"id":"cc"}
```

(해시·txid·time·size·weight는 실행마다 다름. `...`는 생략)

- 최신 블록(102)은 setup 스크립트가 miner → alice, miner → bob 송금을 담아 만든 블록이라 `nTx`가 3입니다(코인베이스 + 송금 2건).
- 첫 트랜잭션의 `vin`에 `coinbase` 필드가 있습니다. 코인베이스 트랜잭션이라는 뜻입니다. 앞부분 `0166`은 블록 높이 102(0x66)입니다(BIP34).
- curl 응답의 세 필드: `result`(결과), `error`(오류, 없으면 null), `id`(요청과 응답을 짝짓는 값, 보낸 "cc" 그대로).

과제 출력 예:

```
== alice·bob이 받은 송금과 담긴 블록 ==
{"wallet":"alice","txid":"77a1a82ba10a33c3611222680d56ffda7c9df9494fe3ca07069e44f337c712f9","amount":5.00000000,"blockheight":102,"blockhash":"1ded3b1e2b5db009d9bc51a47aced0ef8223364c14f6b09e17e0210e8653135c"}
{"wallet":"bob","txid":"bed0f1f16a393be66c9dc2f2286efd831481109f2b1dfe9106f834041d5011da","amount":5.00000000,"blockheight":102,"blockhash":"1ded3b1e2b5db009d9bc51a47aced0ef8223364c14f6b09e17e0210e8653135c"}
== getblock verbosity별 출력 크기 (최신 블록) ==
verbosity 0: 1397 bytes
verbosity 1: 1590 bytes
verbosity 2: 5873 bytes
== 없는 메서드 호출 ==
{"result":null,"error":{"code":-32601,"message":"Method not found"},"id":"cc"}
```

(txid·해시·바이트 수는 실행마다 다름. verbosity 0은 블록 크기의 2배 남짓한 hex 문자열, 2는 트랜잭션을 모두 펼쳐 가장 큼)

## 흔히 막히는 지점

- **지갑 명령에서 지갑을 정할 수 없다는 오류.** miner, alice, bob 세 지갑이 로드되어 있으므로 지갑 명령에는 항상 `-rpcwallet=`을 붙입니다.
- **curl이 `401` 또는 빈 응답.** 쿠키 경로가 틀렸거나, 노드를 다시 켜서 쿠키가 바뀌었습니다. 쿠키는 노드를 켤 때마다 새로 만들어지므로 `COOKIE`를 다시 읽으세요.
- **`cat: .../.cookie: No such file or directory`.** 노드가 꺼져 있거나 데이터 디렉터리 경로가 OS와 다릅니다(macOS는 `~/Library/Application Support/Bitcoin`).
- **다른 환경에서 `getrawtransaction`이 "No such mempool or blockchain transaction".** `txindex`가 없으면 멤풀·지갑 관련 거래, 또는 블록 해시를 함께 준 경우만 조회됩니다. 과정 설정에는 `txindex=1`이 있습니다.
- **슬라이드 명령이 안 됨.** RPC는 버전마다 바뀝니다. `bitcoin-cli -regtest help getblock`으로 현재 버전의 인자를 확인하세요.

## 퀴즈

[quiz/lesson-07.md](../../quiz/lesson-07.md)
