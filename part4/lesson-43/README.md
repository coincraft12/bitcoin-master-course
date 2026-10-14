# lesson-43 · 10-4 초기 블록 다운로드, 10강 미니 과제

## 목표
- IBD의 단계와 주요 병목을 설명한다.
- assumevalid와 assumeUTXO가 무엇을 생략하고 무엇을 검증하는지 설명한다.
- 노드 로그와 RPC로 동기화 진행을 해석한다.

IBD 단계 (s104-stages): 피어 연결(9-1) → 헤더 동기화(2단계 헤더 사전 동기화, Core 24~) → 여러 피어에서 블록 병렬 다운로드 → 순서대로 검증·UTXO 갱신 → 완료. 병목: UTXO 집합 접근(dbcache), 서명 검증(CPU), 디스크·네트워크.
- assumevalid: Core에 박힌 블록 해시의 조상 블록들의 스크립트(서명) 검증만 건너뛴다. 작업량·구조·이중지불·금액 규칙·UTXO 계산은 여전히 검증. 그 해시를 포함한 체인이 최다 작업량일 때만. 끄려면 `assumevalid=0`.
- assumeUTXO: 소스에 해시가 박힌 스냅샷으로 먼저 쓰고, 백그라운드에서 제네시스부터 검증해 일치하면 대체. `dumptxoutset`으로 만들고 `loadtxoutset`으로 불러온다. 메인넷 스냅샷 높이는 Core 28 840,000 · 29 880,000 · 30 910,000(버전마다 갱신).

## 파일
- `sync_snapshot.sh` — 실습 (s104-lab). signet 노드가 있으면 동기화 관찰, regtest로 UTXO 스냅샷
- `assignment/` — 10강 미니 과제 "재조직 보고서" (README, exercise, solution)

## 실습 순서
1. (signet) `getblockchaininfo`의 blocks·headers·verificationprogress·initialblockdownload — 동기화 중이면 headers가 blocks보다 먼저 최신 높이에 있다(헤더 우선).
2. (signet) `debug.log`의 `UpdateTip` 마지막 세 줄에서 progress·cache 값 해석. dbcache를 바꿔 속도 비교는 선택.
3. (regtest) `gettxoutsetinfo`로 height·txouts·total_amount·hash_serialized_3 → `dumptxoutset … latest`로 UTXO 집합 전체를 파일 하나로 → 크기 확인. dumptxoutset 결과의 해시가 gettxoutsetinfo의 해시와 대응하는지 본다.
4. `loadtxoutset`은 실패한다: 우리 regtest 체인은 소스에 등록된 스냅샷 높이·해시와 다르다 → 그 실패가 바로 안전장치.

## 실행
```bash
bash part4/lesson-43/sync_snapshot.sh       # regtest 노드 (signet 노드는 선택)
```
스크립트는 dumptxoutset 전에 `/tmp/utxo_snapshot.dat`를 지운다(이미 있으면 dumptxoutset이 실패한다).

## 기대 출력 (값은 실행마다 다름)
```
(signet 노드 없음 → signet 부분 건너뜀. 띄우려면 bitcoind -signet -daemon)
{
  "height": 316,
  "txouts": 421,
  "total_amount": 11412.50000000,
  "hash_serialized_3": "a3c9…51e0"
}
{
  "coins_written": 421,
  "base_hash": "6e2a…",
  "base_height": 316,
  "path": "/tmp/utxo_snapshot.dat",
  "txoutset_hash": "a3c9…51e0",
  "nchaintx": 452
}
-rw------- 1 user user 31K Oct 14 14:20 /tmp/utxo_snapshot.dat
# 우리 regtest 체인은 소스에 등록된 스냅샷 높이·해시와 달라 loadtxoutset이 실패한다 → 그 실패가 바로 안전장치
error code: -32603
error message:
Unable to load UTXO snapshot: …
→ 예상대로 실패
```
dumptxoutset의 `txoutset_hash`가 gettxoutsetinfo의 `hash_serialized_3`와 같아야 한다. 오류 문구의 나머지는 Core 버전과 상황에 따라 다르다. signet 노드가 있으면 맨 앞에 blocks·headers 네 값과 UpdateTip 세 줄이 나온다.

## 퀴즈
`quiz/lesson-43.md`
