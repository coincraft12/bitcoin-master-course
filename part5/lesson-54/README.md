# lesson-54 · 13-2 라이트닝 실무와 LND 실습

## 목표
- 수탁·LSP 기반·완전 비수탁 지갑의 트레이드오프를 비교한다 (s132-wallets).
- 인보이스(BOLT11)와 오퍼(BOLT12)의 차이를 설명한다 (s132-invoice).
- regtest에서 라이트닝 노드 두 개로 채널을 열고 결제하고 닫는다 (s132-lab1, s132-lab2).

| 유형 | 키·채널 관리 | 장점 | 위험 |
|---|---|---|---|
| 수탁형 | 운영사가 전부 | 쉬움, 즉시 사용 | 운영사 파산·동결·규제. 사실상 운영사 계좌 |
| LSP 기반 비수탁 | 사용자가 키, LSP가 채널·유동성 지원 | 비교적 쉬움, 자기 키 보관 | LSP 의존, 수수료 |
| 완전 비수탁 노드 | 사용자가 노드·채널 직접 운영 | 최대 통제권 | 운영 난이도, 유동성 관리 |

국내에서 이용자 가상자산을 보관·관리하는 수탁형 서비스는 특정금융정보법상 가상자산사업자 신고 대상이 될 수 있다.

- **BOLT11 인보이스** — `lnbc`(regtest는 `lnbcrt`)로 시작. 금액, 결제 해시(13-1의 H), 만료, 받는 노드, 서명. bech32 인코딩(3-4). 한 번만 쓰는 것이 원칙.
- **BOLT12 오퍼** — 재사용 가능한 결제 요청. 고정 QR 하나로 여러 번, 온니언 메시지로 매번 새 인보이스, 블라인드 경로로 받는 노드 정보 숨김. 2024년 9월 사양 병합. 2026년 6월 기준 Core Lightning(v24.11~)·LDK(v0.1~)·Eclair(v0.11.0~) 지원, LND는 네이티브 미지원(별도 LNDK).

수수료 급등과 백업 (s132-fees): 강제 종료 트랜잭션은 미리 서명되어 수수료 변경이 어렵다(→ 앵커 + CPFP 8-4, TRUC 8-5). 작은 HTLC는 온체인 정산 비용이 금액보다 커서 사실상 보호받지 못할 수 있다. 라이트닝은 **시드만으로 복구되지 않는다** — 정적 채널 백업(SCB)은 상대에게 "채널을 닫아 달라"고 요청할 정보뿐. **예전 채널 상태를 백업에서 복원해 올리면 13-1의 처벌을 받을 수 있다.**

## 파일
- `lnd_lab.sh` — 실습 ①~④를 docker exec로 묶은 스크립트 (Polar). `FORCE=1`이면 강제 종료까지. **작성 환경에 Polar·LND가 없어 실행 검증하지 못했다**(bash -n, shellcheck 통과)
- `check_preimage.py` — 결제 영수증 확인 `SHA256(preimage) = payment_hash`. 노드 없이 실행
- `channel_math.py` — 슬라이드 실행 결과 숫자(또는 내 결과)로 잔액이 어디로 갔는지 계산. 노드 없이 실행

## 설치·준비
1. Docker와 [Polar](https://lightningpolar.com) 설치 → 새 네트워크: LND 노드 2개(alice, bob) + Bitcoin Core 1개 → Start.
2. 각 노드의 "Terminal" 버튼으로 셸을 연다. 슬라이드 명령은 모두 이 셸에서 친다.
3. 스크립트로 돌릴 때는 `docker ps`로 컨테이너 이름을 확인하고, 기본값(`polar-n1-alice`, `polar-n1-bob`, `polar-n1-backend1`, RPC 계정 `polaruser`/`polarpass`)과 다르면 환경 변수로 바꾼다:
   ```bash
   ALICE="docker exec <alice 컨테이너> lncli --network=regtest" \
   BOB="docker exec <bob 컨테이너> lncli --network=regtest" \
   BTC="docker exec <bitcoind 컨테이너> bitcoin-cli -regtest -rpcuser=… -rpcpassword=…" \
   BOB_HOST=<bob 컨테이너 호스트 이름> bash part5/lesson-54/lnd_lab.sh
   ```
   호스트에 `jq`와 python3가 있어야 한다(저장소 최상위에서 실행).

## 실습 순서 (슬라이드 명령)
①② 노드 정보, 자금, 채널 열기 (alice 터미널)
```bash
lncli --network=regtest getinfo | jq '{identity_pubkey, block_height, num_active_channels}'
lncli --network=regtest newaddress p2tr
# bitcoind로 alice 주소에 1 BTC 입금 후 블록 6개
BOB_PUB=<bob 노드의 identity_pubkey>
lncli --network=regtest connect $BOB_PUB@<bob 호스트>:9735
lncli --network=regtest openchannel --node_key $BOB_PUB --local_amt 1000000
# 블록 6개 생성 후
lncli --network=regtest listchannels | jq '.channels[] | {channel_point, capacity, local_balance, remote_balance, commitment_type}'
```
`channel_point` = 펀딩 txid:출력 번호 → bitcoind로 조회하면 1,000,000 sat 출력이 P2WSH(2-of-2).

③④ 결제, 그리고 종료
```bash
# bob
lncli --network=regtest addinvoice --amt 25000 --memo "coffee" | jq -r .payment_request
# alice
lncli --network=regtest decodepayreq <인보이스>
lncli --network=regtest payinvoice <인보이스>        # 확인 질문에 yes
lncli --network=regtest listchannels | jq '.channels[] | {local_balance, remote_balance}'
lncli --network=regtest closechannel --funding_txid <txid> --output_index 0
```
`--output_index`는 `channel_point`의 `:` 뒤 숫자다. 슬라이드 상황(1 BTC 입금 → 1,000,000 sat 채널)에서는 펀딩 출력이 잔돈보다 작아 0번이 되지만, 다른 금액이면 1일 수 있다. 스크립트는 `channel_point`에서 읽는다.

시간이 남으면 새 채널을 열고 `closechannel --force` → `pendingchannels`의 `limbo_balance`, `blocks_til_maturity` 144 (13-1의 상대 타임락).

## 기대 출력
슬라이드 실행 결과 (LND 0.21.4 · Core 31.1, 슬라이드 수치)
| 단계 | 결과 |
|---|---|
| 채널 개설 | capacity 1,000,000 · local_balance 996,530 · remote 0 · commitment_type ANCHORS |
| 결제 후 | local 971,530 · remote 25,000 · 블록 수·멤풀 그대로 0건 |
| 영수증 | SHA256(preimage) = payment_hash 일치 |
| 협력 종료 | 출력 2개: 25,000 / 970,175 |
| 강제 종료 | limbo_balance에 alice 몫, blocks_til_maturity 144 |

identity_pubkey, 주소, txid, 인보이스, preimage는 실행마다 다름.

`channel_math.py` (결정적, 직접 실행해 확인)
```
채널 용량                     1,000,000 sat  (펀딩 출력, P2WSH 2-of-2)
개설 직후 local_balance         996,530 sat
  차이                            3,470 sat  = 커밋 수수료 2,810 + 앵커 330 × 2
결제 후 local / remote          971,530 / 25,000 sat  (블록 0개)
협력 종료 출력 합               995,175 sat  = 25,000 + 970,175
협력 종료 실제 수수료             4,825 sat  = 용량 − 출력 합
local_balance − 종료 출력         1,355 sat  = 실제 수수료 4,825 − 커밋 몫 3,470
→ 협력 종료에는 커밋 수수료 예약분과 앵커가 없으므로 그 몫이 개설자(alice)에게 돌아오고,
  종료 수수료는 개설자가 낸다. 그래서 local_balance와 종료 출력의 차이는 실제 수수료보다 작다.
```
슬라이드는 971,530과 970,175의 차이(1,355)를 "종료 수수료"라고 하지만, 종료 트랜잭션의 실제 수수료는 1,000,000 − 995,175 = 4,825 sat이다(ERRATA.md).

`check_preimage.py` (인자 없이, 결정적)
```
시연: preimage = 00 01 02 … 1f (32바이트)
preimage     : 000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
SHA256       : 630dcd2966c4336691125448bbb25b4ff412a49c732db2c8abc1b8581bd710dd
payment_hash : 630dcd2966c4336691125448bbb25b4ff412a49c732db2c8abc1b8581bd710dd
일치         : True
```
실습에서는 `python part5/lesson-54/check_preimage.py <listpayments의 payment_preimage> <decodepayreq의 payment_hash>` → `일치 : True`.

## 흔히 막히는 지점
- 블록을 만들지 않아 채널이 계속 대기(pending) 상태 — 개설 뒤 블록 6개.
- `connect` 실패 — bob 주소는 Polar 내부 호스트 이름과 9735 포트. 이미 연결돼 있으면 오류가 나도 무시해도 된다.
- `lncli: unable to read macaroon` — `--network=regtest`를 빠뜨렸다.
- `payinvoice`가 경로를 못 찾음 — 채널이 아직 active가 아니다(`num_active_channels` 확인).
- 예전 채널 백업을 복원해 상태를 되돌리지 말 것 — 처벌 대상이다.

## 퀴즈
`quiz/lesson-54.md`
