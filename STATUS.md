# STATUS — bitcoin-master-course

> 비트코인 마스터코스(coincraft.io `bitcoin-master-course`, 5부 14강 60차시) 실습 저장소. 원격: github.com/coincraft12/bitcoin-master-course

## 현재 상태
| 항목 | 내용 |
|---|---|
| 단계 | 초판 완성(f820f53, 60차시 코드·README·퀴즈·과제·풀이) + 검토 보완 1커밋(로컬, 미푸시). 강좌 레슨 영상은 아직 없음(coincraft.io STATUS 참고) |
| 검증 | lib 테스트 932 통과·2 건너뜀(coincurve 선택 설치) — Windows 기본 인코딩(cp949)에서도 통과. 노드가 필요한 실습은 미검증 |
| 알려진 한계 | 없음(검토에서 나온 Windows 호환 문제 모두 해결). 노드 연동 실습만 미검증 |

## 마지막 작업 (2026-10-14)
- 전체 검토: 차시 60개 README·퀴즈 60개·README 링크 60개 유효, py 125개 문법·sh 50개 `bash -n` 통과, 시크릿 없음, 풀이 스크립트 정상
- `.gitattributes` 추가(`* text=auto eol=lf`, BIP340 csv는 `-text`) — Windows 클론에서 단어장 해시 테스트 실패·sh CRLF 방지
- `open()`·`read_text`·`write_text` 73곳에 `encoding="utf-8"` 지정(37파일, 바이너리 모드·BIP 참조 구현 `musig2/reference.py` 제외) — cp949 환경 테스트 수집 오류 해소
- `lib/__init__.py`가 import 시 stdout·stderr를 UTF-8로 맞춤(cp949 리디렉션에서 − ≈ ‖ 출력 실패하던 스크립트 9개 해결, 슬라이드 기대 출력 유지, `channel_math.py`에 `import lib` 추가)
- `tests/test_ripemd160.py`(공식 벡터 8개)·`tests/test_rpc.py`(가짜 응답으로 쿠키·URL·오류·Decimal·금액 변환) 추가
- README: `coincurve` 선택 설치 안내, `requirements.txt`에 선택 항목 주석, `txoutproof.py` 인자 없을 때 사용법 출력
- 미검증: Bitcoin Core가 이 PC에 없어 노드 연동 py·쉘 실습(regtest·signet·Polar) 실행 확인은 못 함

## 다음 작업
- [ ] 노드가 있는 환경에서 `env/setup_regtest.sh` → 1~5부 실습 스크립트·쉘 랩 일괄 실행 검증
- [ ] 검토 보완 커밋 푸시(Sharon 확인 후)
