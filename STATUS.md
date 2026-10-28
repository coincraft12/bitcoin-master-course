# STATUS — bitcoin-master-course

> 비트코인 마스터코스(coincraft.io `bitcoin-master-course`, 5부 14강 60차시) 실습 저장소. 원격: github.com/coincraft12/bitcoin-master-course

## 현재 상태
| 항목 | 내용 |
|---|---|
| 단계 | 초판 완성(f820f53, 60차시 코드·README·퀴즈·과제·풀이) + 검토·실행 검증 보완 2커밋(푸시 완료, b50acb3). 강좌 레슨 영상은 아직 없음(coincraft.io STATUS 참고) |
| 검증 | lib 테스트 932 통과·2 건너뜀(coincurve 선택) — cp949에서도 통과. **regtest 쉘 랩 48개 중 46개 실행, 45개 완전 통과**(Core 31.1, Docker; `watch_spread`는 1~2단계만). 미검증: Polar(LND) 랩·메인넷·signet |
| 알려진 한계 | `MUSIG=1` 볼트(최종 프로젝트)는 키 경로 대신 스크립트 경로로 송금(ERRATA 참고) · 노드 연동 py 일부는 개별 실행 안 함 |

## 마지막 작업 (2026-10-28)
- 촬영 리허설(Windows 네이티브 Core 31.1, PowerShell 5.1): 4-4·5강 실습 전 구간 실행 검증, 3·6~14강은 강별 에이전트가 전용 regtest 노드로 대본·슬라이드 명령을 실행해 교정(대본은 `_Archive/.../나레이션`, 이 저장소 밖)
- 저장소 보완(미커밋): `part3/lesson-20/verify_with_core.py` Windows용 RPC 폴백, `part2/lesson-17/README.md` `watchonly`→`mine.trusted`, ERRATA `s52-verify`
- 실행에서 드러난 저장소 쪽 문제(미수정, 아래 다음 작업): `lib/rpc.py` regtest 포트 18443·`~/.bitcoin` 고정, 8강 과제 정답이 `send`로 자식을 만들어 README 기대값 10.20 미재현(실측 27.00), `coinbase_tags.py` 비율 열 `n/10` 고정, `.sh`의 `python3`(Windows 스토어 스텁), 12강 `tamper_psbt.py`(sign=false 방식)와 대본 방식 차이, `vault_descriptor.sh spend()`의 `.[0]`

## 다음 작업
- [x] 검토·검증 보완 커밋 푸시 완료 (Claude Co-Authored-By 줄 제거 후 force-push)
- [ ] `MUSIG=1` 볼트: 서명 지갑에 `musig()` 디스크립터를 가져오게 구성 변경 후 키 경로 witness(64바이트) 확인
- [ ] Polar(LND) 실습(`part5/lesson-54/lnd_lab.sh`)·메인넷 조회(`fork_points.sh`)·signet 실습 검증
- [ ] 수강생용 Docker 단일 명령 regtest 환경(`env/`) 추가 여부 결정 — 이번 검증에 쓴 래퍼(`bitcoin-cli`·`bitcoind` 셸 스크립트)가 출발점
- [ ] ERRATA 3종을 강의 슬라이드·PDF에도 반영(슬라이드 id: s35-lab·s81-lab·s83-lab·s92-lab1·s93-lab·s14-final)
- [ ] (10/28 검증에서 발견) `lib/rpc.py`가 환경변수로 포트·데이터 디렉터리를 받도록 수정 · 8강 과제 정답/README 기대값 정합 · `coinbase_tags.py` 비율 열 · `.sh`의 `python3` 대체 · `vault_descriptor.sh spend()`의 `listunspent .[0]`
- [ ] 이 10/28 변경(위 3개 파일 + ERRATA)과 위 수정 커밋 시 STATUS를 같은 커밋에 포함
