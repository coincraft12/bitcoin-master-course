# lesson-39 · 9-3 경량 클라이언트와 네트워크 프라이버시, 9강 미니 과제

## 목표
- SPV, 블룸 필터, 블록 필터, 서버 질의 방식을 비교한다.
- 각 방식이 무엇을 검증하고 무엇을 노출하는지 설명한다.
- Tor·I2P·v2 암호화 전송을 설정하고 확인한다.

| 방식 | 동작 | 프라이버시 | 현황 |
|---|---|---|---|
| 블룸 필터 (BIP37) | "내 주소들" 필터를 노드에 보내고 노드가 골라 줌 | 주소가 상당 부분 드러남. 노드 DoS 부담 | Core 기본 비활성 |
| 블록 필터 (BIP157/158) | 노드가 블록마다 필터 공개, 지갑이 직접 일치 판단 후 필요한 블록만 | 노드는 지갑이 무엇을 찾는지 모름 | 일부 지갑, LND Neutrino |
| 서버 질의 (Electrum 등) | 지갑이 주소·스크립트 목록을 서버에 직접 질의 | 서버가 모든 주소를 앎 | 가장 널리 쓰임 |

블록 필터: 블록마다 등장하는 출력 스크립트들을 골롬 코딩 필터로 압축 → 지갑이 로컬에서 확인 → 거짓 양성은 블록을 받아 확인하면 된다.

## 파일
- `filter_size.py` — Core 테스트 데이터(testnet3 블록 10개)로 블록 vs 필터 크기, 필터 헤더 사슬 검증 (노드 없이)
- `filters_v2.sh` — 실습 01·02·03 (s93-lab). signet 노드가 있으면 signet 필터도 본다
- `assignment/` — 9강 미니 과제 "내 노드 네트워크 보고서" (README, exercise, solution)

## 실습 순서 (s93-lab)
1. 최신 블록 필터 조회 → 블록보다 훨씬 작은 크기 확인 (2-1 bitcoin.conf의 `blockfilterindex=1`). 인덱스가 아직 동기화되지 않았으면 `getindexinfo`부터 본다.
2. 9-2 2노드 환경에서 `transport_protocol_type`이 v2인지 확인 → node2를 `-v2transport=0`으로 재시작해 v1과 비교.
3. (선택, 메인넷·signet) Tor 설정 → `getnetworkinfo`의 `localaddresses`에 onion 주소.

## 실행
```bash
python part4/lesson-39/filter_size.py
bash   part4/lesson-38/two_nodes.sh       # 2노드 환경 (lesson-38)
bash   part4/lesson-39/filters_v2.sh
```

## 기대 출력
`filter_size.py` (결정적)
```
      높이    블록(B)    필터(B)     비율  헤더 검증  비고
       0      285        4   71.2        OK  Genesis block
       2      190        4   47.5        OK  
       3      190        4   47.5        OK  
   15007      190        4   47.5        OK  Tx has non-standard OP_RETURN output fol
   49291     1597       28   57.0        OK  Tx pays to empty output script
  180480     1344       35   38.4        OK  Tx spends from empty output script
  926485     1982       25   79.3        OK  Duplicate pushdata 913bcc2be49cb534c2047
  987876      193        4   48.2        OK  Coinbase tx has unparseable output scrip
 1263442      518        9   57.6        OK  Includes witness data
 1414221      165        1  165.0        OK  Empty data
합계: 블록 6654 B, 필터 118 B (56배 작다)
```
필터 헤더 = dsha256(dsha256(필터) ‖ 이전 필터 헤더). `getblockfilter`의 `header`가 이 값이다. 이 테스트 블록들은 트랜잭션이 적어 작지만, 수 MB 메인넷 블록에서도 필터는 수십 KB 수준이다.

`filters_v2.sh` (해시·필터는 실행마다 다름)
```
######## 01 최신 블록 필터 ########
{
  "filter": "01a8e5c0",
  "header": "6d4b…f2a1"
}
{
  "txindex": { "synced": true, "best_block_height": 313 },
  "basic block filter index": { "synced": true, "best_block_height": 313 }
}
블록 248 바이트 vs 필터 5 바이트 (줄바꿈 1글자 포함 근사)
######## 02 v2 전송 확인 (9-2 2노드 환경에서) ########
{ "addr": "127.0.0.1:18555", "transport_protocol_type": "v2" }
{ "addr": "127.0.0.1:18555", "transport_protocol_type": "v1" }
→ 다음 실습(10-3)을 위해 node2를 기본 설정으로 되돌리려면:
   bash part4/lesson-38/two_nodes.sh stop && bash part4/lesson-38/two_nodes.sh
```
regtest 블록은 코인베이스 하나뿐이라 작다. 필터 크기 차이를 실감하려면 signet 노드로 본다.

## 퀴즈
`quiz/lesson-39.md`
