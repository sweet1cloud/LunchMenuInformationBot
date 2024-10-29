# LunchMenuInformationBot
1. 학교 급식 메뉴를 알려주는 디스코드 봇입니다.<br/>
2. [나이스(NEIS) 교육정보 개방 포털](https://open.neis.go.kr/portal/data/service/selectServicePage.do?page=1&rows=10&sortColumn=&sortDirection=&infId=OPEN17320190722180924242823&infSeq=1)의 '급식식단정보' API를 사용하였습니다.<br/>
3. API를 사용하기 전 나이스 교육정보 개방 포털에서 인증키를 신청하여 API 키를 먼저 발급하셔야 합니다.<br/>
4. 명령어는 슬래시(/)와 기존 Prefix 명령어(!)를 모두 사용할 수 있도록 작성하였습니다.
5. app.py 파일은 ChatGPT의 도움을 받아 코드를 작성하였습니다.
6. 현재는 봇이 중식 메뉴만 알려주도록 되어 있습니다. 조식이나 석식 메뉴는 'MMEAL_SC_CODE'에 조식 코드('1')나 석식 코드('3')을 추가하시면 됩니다.
