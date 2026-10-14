# STATUS — bitcoin-master-course

> 비트코인 마스터코스(coincraft.io `bitcoin-master-course`, 5부 14강 60차시) 실습 저장소. 원격: github.com/coincraft12/bitcoin-master-course

## 현재 상태
| 항목 | 내용 |
|---|---|
| 단계 | 초판 완성(f820f53, 60차시 코드·README·퀴즈·과제·풀이) + 검토·실행 검증 보완 2커밋(푸시 완료, b50acb3). 강좌 레슨 영상은 아직 없음(coincraft.io STATUS 참고) |
| 검증 | lib 테스트 932 통과·2 건너뜀(coincurve 선택) — cp949에서도 통과. **regtest 쉘 랩 48개 중 46개 실행, 45개 완전 통과**(Core 31.1, Docker; `watch_spread`는 1~2단계만). 미검증: Polar(LND) 랩·메인넷·signet |
| 알려진 한계 | `MUSIG=1` 볼트(최종 프로젝트)는 키 경로 대신 스크립트 경로로 송금(ERRATA 참고) · 노드 연동 py 일부는 개별 실행 안 함 |

## 마지막 작업 (2026-10-14~15)
- 전체 검토: 구조·README·퀴즈·문법·테스트 점검, Windows 호환(`.gitattributes` LF, `open()` utf-8 73곳, `lib/__init__.py` stdout UTF-8), `rpc`·`ripemd160` 테스트 추가
- Docker(bitcoin/bitcoin:31.1)로 regtest 노드를 띄워 쉘 랩을 차시 순서대로 실행: `lesson-02`~`60` 단일 노드 랩 전부 + 노드 2개 랩(two_nodes·watch_spread·reorg·filters_v2) + submitpackage·testdummy(reset 후) 통과. `lnd_lab`(Polar)·`fork_points`(메인넷)는 미실행
- 랩에서 레포 결함 3종 수정(ERRATA.md 기록): ① `gettransaction … true` → `false true`(measure_sizes·fee_lab·rbf_lab) ② node2 `-port=18555 -rpcport=18556`이 Tor 리스너와 충돌 → `-bind=0.0.0.0:18555`(two_nodes·filters_v2) ③ vault_wallet 복구 경로 UTXO 선택 `max_by(.amount)` + `\r` 제거
- 환경 문제는 레포 문제가 아님(이 PC 한정): `python3`가 스토어 스텁, Git Bash의 `/tmp` 경로 변환, node2 로그 파일이 컨테이너 안에 있어 `watch_spread.sh` 3단계(grep)는 건너뜀
- 코드 수정 없는 미해결: `vault_wallet.sh MUSIG=1`(서명 지갑에 `musig()` 디스크립터 필요)

## 다음 작업
- [x] 검토·검증 보완 커밋 푸시 완료 (Claude Co-Authored-By 줄 제거 후 force-push)
- [ ] `MUSIG=1` 볼트: 서명 지갑에 `musig()` 디스크립터를 가져오게 구성 변경 후 키 경로 witness(64바이트) 확인
- [ ] Polar(LND) 실습(`part5/lesson-54/lnd_lab.sh`)·메인넷 조회(`fork_points.sh`)·signet 실습 검증
- [ ] 수강생용 Docker 단일 명령 regtest 환경(`env/`) 추가 여부 결정 — 이번 검증에 쓴 래퍼(`bitcoin-cli`·`bitcoind` 셸 스크립트)가 출발점
- [ ] ERRATA 3종을 강의 슬라이드·PDF에도 반영(슬라이드 id: s35-lab·s81-lab·s83-lab·s92-lab1·s93-lab·s14-final)
