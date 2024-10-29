#ChatGPT의 도움을 받아 코드를 작성하였습니다.
import discord
import requests
from discord.ext import commands, tasks
from datetime import datetime, timedelta

# 봇 토큰과 채널 ID
TOKEN = 'YOUR_TOKEN' #봇 토큰 입력
API_KEY = 'YOUR_API_KEY' #나이스 교육정보 개방 포털에서 발급받은 API 키 입력
CHANNEL_ID = YOUR_CHANNEL_ID  # 숫자로 된 디스코드 채널 ID 입력
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# NEIS API 엔드포인트 및 파라미터 설정
API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
PARAMS = {
    'ATPT_OFCDC_SC_CODE': 'N10',  # 지역 교육청 코드
    'SD_SCHUL_CODE': '8140109',  # 학교 코드
    'MMEAL_SC_CODE': '2',  # 중식 코드
    'MLSV_FROM_YMD': '20240101',  # 검색 시작 날짜
    'MLSV_TO_YMD': '20241231',  # 검색 종료 날짜
    'Type': 'json'  # 응답 형식
}

# 알레르기 매핑 정보
allergy_mapping = {
    '1': '난류',
    '2': '우유',
    '3': '메밀',
    '4': '땅콩',
    '5': '대두',
    '6': '밀',
    '7': '고등어',
    '8': '게',
    '9': '새우',
    '10': '돼지고기',
    '11': '복숭아',
    '12': '토마토',
    '13': '아황산류',
    '14': '호두',
    '15': '닭고기',
    '16': '쇠고기',
    '17': '오징어',
    '18': '조개류',
}

# 요일 한글 매핑
weekdays_korean = {
    'Monday': '(월)',
    'Tuesday': '(화)',
    'Wednesday': '(수)',
    'Thursday': '(목)',
    'Friday': '(금)',
    'Saturday': '(토)',
    'Sunday': '(일)'
}

#메시지 자동 전송 작업은 아직 연구 중인 부분입니다.
# 매일 아침 8시에 자동으로 메시지를 전송하는 작업
@tasks.loop(hours=24)  # 24시간 주기로 실행
async def send_daily_lunch_menu():
    now = datetime.now()
    # 매일 8시에 실행되도록 설정
    target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

    # 오늘 8시가 지나면 내일 8시로 설정
    if now > target_time:
        target_time += timedelta(days=1)

    wait_time = (target_time - now).total_seconds()
    await discord.utils.sleep_until(target_time)

    # 메세지 전송 부분
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("아침 급식 메뉴를 확인하세요!")  # 여기에 실제 급식 메뉴를 추가해야 함

@bot.event
async def on_ready():
    await bot.tree.sync()  # 슬래시 커맨드 등록
    print("슬래시 커맨드가 등록되었습니다.")  # 추가된 로그
    send_daily_lunch_menu.start()  # 봇이 준비되면 작업 시작
    print(f'We have logged in as {bot.user}')

@bot.command(name='shutdown', help='봇을 종료합니다.') #유저들이 사용할 수 있는 슬래시(/) 대신 기존 명령어(!)로 종료
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("봇이 종료됩니다...")
    await bot.close()  # 봇을 안전하게 종료합니다.

# 슬래시 커맨드 및 일반 명령어 정의 (예: lunch, allergy)

# 슬래시 커맨드
@bot.tree.command(name='lunch', description='오늘의 중식 메뉴를 조회합니다.')
async def send_lunch_menu_slash(interaction: discord.Interaction,
                                date: str = None):
    if date is None:
        date = datetime.today().strftime('%Y%m%d')  # 기본값으로 오늘 날짜 사용

    # 요일 구하기
    day_of_week = datetime.strptime(date, '%Y%m%d').strftime('%A')
    day_of_week_korean = weekdays_korean.get(day_of_week, '')  # 한글 요일 가져오기

    try:
        # API 호출
        PARAMS['MLSV_FROM_YMD'] = date
        PARAMS['MLSV_TO_YMD'] = date
        response = requests.get(API_URL, params=PARAMS)

        # JSON 형식으로 파싱
        data = response.json()

        # 디버깅: 받아온 데이터 출력
        print(data)

        # 급식 정보 확인
        if 'mealServiceDietInfo' in data:
            meal_info = data['mealServiceDietInfo'][1]['row'][0]
            date_info = meal_info['MLSV_YMD']
            if 'DDISH_NM' in meal_info:
                menu_items = meal_info['DDISH_NM'].replace('<br/>',
                                                           '\n').splitlines()
                response_message = f"{date_info} {day_of_week_korean} 중식 메뉴:\n"

                for menu in menu_items:
                    response_message += f"{menu}\n"

                await interaction.response.send_message(response_message)
            else:
                await interaction.response.send_message("해당 날짜에 중식 정보가 없습니다.")
        else:
            await interaction.response.send_message("급식 정보가 없습니다.")
    except requests.exceptions.RequestException as e:
        await interaction.response.send_message("API 요청에 실패했습니다.")
        print(f"RequestException: {e}")
    except (KeyError, IndexError) as e:
        await interaction.response.send_message("급식 정보를 가져오는 데 실패했습니다.")
        print(f"Data Parsing Error: {e}")
    except ValueError as e:
        await interaction.response.send_message("JSON 형식 변환 오류가 발생했습니다.")
        print(f"JSONDecodeError: {e}")


# 일반 명령어
@bot.command(name='lunch', help='오늘의 중식 메뉴를 조회합니다.')
async def send_lunch_menu_text(ctx, date: str = None):
    if date is None:
        date = datetime.today().strftime('%Y%m%d')  # 기본값으로 오늘 날짜 사용

    # 요일 구하기
    day_of_week = datetime.strptime(date, '%Y%m%d').strftime('%A')
    day_of_week_korean = weekdays_korean.get(day_of_week, '')  # 한글 요일 가져오기

    try:
        # API 호출
        PARAMS['MLSV_FROM_YMD'] = date
        PARAMS['MLSV_TO_YMD'] = date
        response = requests.get(API_URL, params=PARAMS)

        # JSON 형식으로 파싱
        data = response.json()

        # 디버깅: 받아온 데이터 출력
        print(data)

        # 급식 정보 확인
        if 'mealServiceDietInfo' in data:
            meal_info = data['mealServiceDietInfo'][1]['row'][0]
            date_info = meal_info['MLSV_YMD']
            if 'DDISH_NM' in meal_info:
                menu_items = meal_info['DDISH_NM'].replace('<br/>',
                                                           '\n').splitlines()
                response_message = f"{date_info} {day_of_week_korean} 중식 메뉴:\n"

                for menu in menu_items:
                    response_message += f"{menu}\n"

                await ctx.send(response_message)
            else:
                await ctx.send("해당 날짜에 중식 정보가 없습니다.")
        else:
            await ctx.send("급식 정보가 없습니다.")
    except requests.exceptions.RequestException as e:
        await ctx.send("API 요청에 실패했습니다.")
        print(f"RequestException: {e}")
    except (KeyError, IndexError) as e:
        await ctx.send("급식 정보를 가져오는 데 실패했습니다.")
        print(f"Data Parsing Error: {e}")
    except ValueError as e:
        await ctx.send("JSON 형식 변환 오류가 발생했습니다.")
        print(f"JSONDecodeError: {e}")

@bot.tree.command(name='allergy', description='알레르기 정보를 조회합니다.')
async def allergy_info(interaction: discord.Interaction):
    # 알레르기 정보를 표시할 문자열 초기화
    allergy_list = "\n".join([f"{key}: {value}" for key, value in allergy_mapping.items()])

    # 사용자에게 알레르기 정보를 포함한 메시지 전송
    await interaction.response.send_message(f"알레르기 정보:\n{allergy_list}")

@bot.command(name='allergy', help='알레르기 정보를 조회합니다.')
async def allergy_info(ctx):
    # 알레르기 정보를 표시할 문자열 초기화
    allergy_list = "\n".join([f"{key}: {value}" for key, value in allergy_mapping.items()])

    # 사용자에게 알레르기 정보를 포함한 메시지 전송
    await ctx.send(f"알레르기 정보:\n{allergy_list}")

bot.run(TOKEN)
