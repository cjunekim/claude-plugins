# Inspection snapshot — `nvidia/Nemotron-Personas-Korea`

> **Frozen at SHA `d0a9272116a2ebf139b964ca72b8b8f604616689`, captured 2026-05-05.**
>
> This is a SHA-pinned snapshot, not a live spec. The HF dataset can be revised; if the live SHA differs from the one above, re-run `scripts/inspect_dataset.py` and diff before trusting these numbers. The script writes its output in the same shape as this file, so a side-by-side diff is meaningful.

---

## dataset SHA

sha = `d0a9272116a2ebf139b964ca72b8b8f604616689`

## loading dataset

rows = 1,000,000

## schema

```
uuid                            str
professional_persona            str
sports_persona                  str
arts_persona                    str
travel_persona                  str
culinary_persona                str
family_persona                  str
persona                         str
cultural_background             str
skills_and_expertise            str
skills_and_expertise_list       str
hobbies_and_interests           str
hobbies_and_interests_list      str
career_goals_and_ambitions      str
sex                             str
age                           int64
marital_status                  str
military_status                 str
family_type                     str
housing_type                    str
education_level                 str
bachelors_field                 str
occupation                      str
district                        str
province                        str
country                         str
dtype: object
```

columns (26):
```
['uuid', 'professional_persona', 'sports_persona', 'arts_persona', 'travel_persona', 'culinary_persona', 'family_persona', 'persona', 'cultural_background', 'skills_and_expertise', 'skills_and_expertise_list', 'hobbies_and_interests', 'hobbies_and_interests_list', 'career_goals_and_ambitions', 'sex', 'age', 'marital_status', 'military_status', 'family_type', 'housing_type', 'education_level', 'bachelors_field', 'occupation', 'district', 'province', 'country']
```

## assumed columns present?

- missing assumed: `none`
- unaccounted-for in dataset (likely narrative or metadata fields): `['uuid', 'professional_persona', 'sports_persona', 'arts_persona', 'travel_persona', 'culinary_persona', 'family_persona', 'cultural_background', 'skills_and_expertise', 'skills_and_expertise_list', 'hobbies_and_interests', 'hobbies_and_interests_list', 'career_goals_and_ambitions', 'military_status', 'bachelors_field', 'country']`

## `age` column structure

- dtype: `int64`
- head(10):
```
0    74
1    71
2    73
3    46
4    50
5    33
6    31
7    76
8    44
9    27
```
- numeric — `describe()`:
```
count    1000000.000000
mean          50.660031
std           17.612993
min           19.000000
25%           36.000000
50%           51.000000
75%           64.000000
max           99.000000
Name: age, dtype: float64
```

## text-field length comparison

Identifies the compact `persona` summary vs the long narrative fields.

```
```

## 3 random rows — full dump


### row index 157105

```
uuid                          : a28368a0f2ad4977b3ceed93aaae9a68
professional_persona          : 김혜경 씨는 교육학 전공자의 꼼꼼함으로 지역 도서관에서 아이들에게 구연동화를 읽어주는 봉사활동에 매진하며, 손주들에게 물려줄 문경의 옛이야기를 수집해 낡은 수첩에 정성껏 기록하고 있습니다. 마을 부녀회 일정을 조율하는 살림꾼 역할을 도맡아 하지만, 가끔 지나치게 세세한 부분까지 챙기려는 완벽주의 성향 때문에 주변 사람들을 조금 피곤하게 만들기도 합니다.
sports_persona                : 김혜경 씨는 남편의 손을 잡고 문경새재의 흙길을 천천히 밟으며 계절의 변화를 온몸으로 느끼는 산책을 가장 즐기며, 주말이면 동네 친구들과 함께 지역 사우나에서 뜨거운 탕에 몸을 담그고 한 주간의 피로를 풉니다. 격렬한 운동보다는 정적인 움직임을 좋아하며, 걷기 운동 중에 발견한 예쁜 야생화를 사진으로 남기느라 정작 운동 목표량은 채우지 못한 채 돌아오곤 합...[truncated]
arts_persona                  : 김혜경 씨는 스마트폰 카메라 기능을 익혀 숲속의 단풍이나 눈 덮인 산등성이를 촬영해 가족 단체 채팅방에 공유하며, 주말 저녁에는 거실 소파에 기대어 최신 드라마의 반전 전개에 몰입하며 다음 회차를 손꼽아 기다립니다. 교육학 전공자답게 읽기 쉬운 동화책을 소리 내어 읽는 법을 연구하며, 조용히 서재에서 마을의 전설이 담긴 오래된 책들을 탐독하는 시간을 소중히...[truncated]
travel_persona                : 김혜경 씨는 자녀들이 운전하는 차를 타고 전국의 유명한 수목원이나 산책로를 찾아다니며 자연의 풍경을 감상하는 여행을 즐기며, 여행지마다 그 지역의 특산물이 가득 담긴 전통시장을 들러 지인들에게 나눠줄 선물을 고릅니다. 화려한 호텔보다는 풍경이 좋은 한옥 민박에서 가족들과 옹기종기 모여 앉아 밤늦게까지 이야기를 나누는 소박한 여정을 선호합니다.
culinary_persona              : 김혜경 씨는 일주일에 두세 번 동네 단골 분식집에 들러 매콤한 떡볶이와 속이 꽉 찬 김밥을 나눠 먹으며 수다를 떠는 시간을 가장 행복해하며, 외식을 할 때는 고기구이보다는 정갈한 나물 반찬이 나오는 보리밥집을 주로 찾습니다. 가끔 요리하기 귀찮은 날에는 남편과 함께 배달 서비스로 찜닭이나 잡채 같은 한식 메뉴를 주문해 먹으며, 배달 기사님께 따뜻한 캔커피 ...[truncated]
family_persona                : 김혜경 씨는 무뚝뚝한 경북 남성인 남편과 수십 년을 함께 살며 서로의 눈빛만 봐도 무엇을 원하는지 아는 편안한 관계를 유지하고, 가끔 방문하는 손주들을 위해 정성껏 끓인 소고기뭇국과 잡채를 상다리가 휘어지게 차려냅니다. 예의를 중시하는 성격 탓에 며느리나 사위 앞에서는 다정한 시어머니가 되려 노력하지만, 가끔은 은연중에 보수적인 가치관이 튀어나와 잔소리를 ...[truncated]
persona                       : 김혜경 씨는 문경새재의 자연과 이웃의 정을 사랑하며, 교육학적 소양과 보수적인 태도가 공존하는 온화한 성품의 60대 여성입니다.
cultural_background           : 문경새재 근처에서 오랫동안 거주하며 이웃과 넉넉하게 나누는 정 문화를 몸소 익혔습니다. 교육학을 전공한 지적인 배경과 경북 지역 특유의 단단하고 보수적인 생활 태도가 공존하며, 예의와 격식을 중요하게 여기는 편입니다.
skills_and_expertise          : 복잡한 집안 살림과 지역 사회 모임의 일정을 빈틈없이 정리하고 조율하는 능력이 능숙합니다. 상대방의 이야기를 경청하며 갈등이 생겼을 때 부드럽게 중재하여 원만한 합의점을 찾아내는 말솜씨를 갖추고 있습니다.
skills_and_expertise_list     : ['지역 사회 모임 일정 및 회계 관리', '효율적인 주거 공간 수납 및 정리', '세대 간 갈등 중재 및 상담', '제철 식재료를 활용한 나물 요리']
hobbies_and_interests         : 주말마다 남편과 함께 문경새재 숲길을 천천히 걸으며 계절마다 변하는 나무의 색깔을 사진으로 기록합니다. 동네 친구들과 단골 분식집에서 떡볶이와 김밥을 나누어 먹으며 최근 방영하는 주말 드라마의 전개에 대해 열띤 대화를 나눕니다.
hobbies_and_interests_list    : ['문경새재 숲길 사진 촬영', '동네 목욕탕에서의 친목 도모', '주말 가족 드라마 시청 및 분석', '지역 사찰 방문 및 명상', '가족과 함께하는 전국 자연 경관 여행']
career_goals_and_ambitions    : 거창한 사회적 성취보다는 손주들에게 들려줄 마을의 옛이야기를 정리해 작은 책자로 엮어보고 싶어 합니다. 지역 도서관에서 아이들에게 책을 읽어주는 봉사를 하며 소소하게 보람을 찾는 삶을 지향합니다.
sex                           : 여자
age                           : 62
marital_status                : 배우자있음
military_status               : 비현역
family_type                   : 배우자와 거주
housing_type                  : 단독주택
education_level               : 4년제 대학교
bachelors_field               : 교육
occupation                    : 무직
district                      : 경상북-문경시
province                      : 경상북
country                       : 대한민국
```

### row index 374554

```
uuid                          : ce7fdcd68d7540c28e5865b2a79ed68f
professional_persona          : 신연주 씨는 철도 운행 현장에서 발생하는 돌발 상황이나 승객들의 까다로운 요구를 유연하게 해결하는 능력이 뛰어나 동료들의 신뢰를 받습니다. 신연주 씨는 다만 꼼꼼한 서류 작업이나 엑셀 정리에서는 자주 오타를 내어 뒤처리를 부탁해야 하는 서툰 구석이 있습니다.
sports_persona                : 신연주 씨는 평일 저녁이면 마곡역 인근의 필라테스 스튜디오에서 코어 근육을 잡으며 몸의 균형을 맞추는 시간으로 활력을 얻습니다. 신연주 씨는 가끔 머릿속을 비우고 싶을 때 집 근처 서울식물원 산책로를 천천히 걸으며 계절의 변화를 몸소 느낍니다.
arts_persona                  : 신연주 씨는 주말이면 대학로의 작은 소극장을 찾아 배우들의 숨소리가 들리는 연극 한 편을 보며 일상의 무료함을 달랩니다. 신연주 씨는 공연이 끝난 뒤 프로그램 북 귀퉁이에 짧은 감상평을 적어 내려가며 그날의 여운을 기록하는 버릇이 있습니다.
travel_persona                : 신연주 씨는 친한 친구와 함께 강원도 평창의 오대산 전나무 숲길을 걸으며 울창한 초록색 풍경 속에 파묻히는 시간을 가장 아낍니다. 신연주 씨는 세부적인 여행 일정표를 짜기보다 발길 닿는 대로 걷다가 마음에 드는 벤치가 나오면 한참을 멍하니 앉아 자연을 감상합니다.
culinary_persona              : 신연주 씨는 퇴근길 동네 빵집에서 갓 구워 나온 고소한 소금빵을 사 들고 들어가는 소소한 루틴으로 하루의 보상을 받습니다. 신연주 씨는 주말이면 지인들과 함께 두툼한 삼겹살을 굽는 고깃집에서 시끌벅적하게 수다를 떨며 스트레스를 해소합니다.
family_persona                : 신연주 씨는 강서구의 조용한 다세대 주택에서 혼자 거주하며 누구의 간섭도 받지 않는 완전한 독립 공간의 자유를 만끽합니다. 신연주 씨는 밖에서는 서비스 전공자답게 타인의 기분을 세심하게 살피며 다정하게 굴지만, 현관문을 닫는 순간 모든 사회적 가면을 벗고 오직 자신만의 고요함 속에 침잠합니다.
persona                       : 신연주 씨는 철도 운송 현장의 유연한 대처 능력과 개인의 안온한 일상을 조화롭게 가꾸어 나가는 서른한 살의 직장인입니다.
cultural_background           : 강서구 마곡지구 인근의 다세대 주택에서 혼자 살며, 퇴근길에 동네 빵집에서 갓 나온 소금빵을 사들고 들어가는 소소한 일상을 즐깁니다. 서비스 전공을 통해 익힌 배려심 덕분에 주변 사람들에게 다정하다는 말을 자주 듣지만, 정작 자신의 속마음은 갈무리한 채 타인의 기분에 맞추느라 에너지를 소진할 때가 있습니다.
skills_and_expertise          : 철도 운행 현장의 갑작스러운 변동이나 승객들의 돌발 요청에도 당황하지 않고 유연하게 상황을 정리하며 안내합니다. 꼼꼼한 서류 작업에는 서툴러 가끔 실수를 하지만, 현장에서 사람들의 불편함을 빠르게 포착해 해결하는 감각은 동료들 사이에서도 인정받습니다.
skills_and_expertise_list     : ['철도 운송 현장 돌발 상황 대처', '다양한 연령대 승객 응대 및 커뮤니케이션', '열차 운행 스케줄 관리', '현장 서비스 동선 최적화']
hobbies_and_interests         : 주말이면 대학로의 작은 소극장 연극을 보러 가거나, 평일 저녁에는 기구 필라테스로 뭉친 근육을 풀며 하루의 긴장을 덜어냅니다. 가끔 친구와 함께 강원도 평창의 울창한 숲길을 걸으며 초록색 풍경 속에 파묻혀 머릿속을 비우는 시간을 갖습니다.
hobbies_and_interests_list    : ['대학로 소극장 연극 관람', '기구 필라테스', '평창 숲길 트레킹', '동네 사우나에서 반신욕 하기']
career_goals_and_ambitions    : 거창한 직함이나 승진보다는 현재의 안정적인 소득을 유지하며 업무 스트레스가 일상을 잠식하지 않는 균형 잡힌 삶을 지향합니다. 현장에서 겪은 경험을 바탕으로 승객들이 실제로 체감할 수 있는 작은 편의 시설 개선 아이디어를 제안해보고 싶어 합니다.
sex                           : 여자
age                           : 31
marital_status                : 미혼
military_status               : 비현역
family_type                   : 혼자 거주
housing_type                  : 다세대주택
education_level               : 4년제 대학교
bachelors_field               : 서비스
occupation                    : 철도운송 관련 종사원
district                      : 서울-강서구
province                      : 서울
country                       : 대한민국
```

### row index 688694

```
uuid                          : 15c96975ea044800b38a9a27caf916b6
professional_persona          : 김대훈 씨는 김해의 법률 사무소에서 복잡한 서류 뭉치를 빠르게 처리하며 의뢰인의 불안한 마음을 능숙한 말솜씨로 달래는 실무 전문가입니다. 규정의 빈틈을 찾아 효율적인 길을 제시하는 유연함이 있지만, 정작 본인의 책상 위 서류 정리만큼은 늘 내일로 미뤄두는 습관이 있습니다.
sports_persona                : 김대훈 씨는 주말이면 사직야구장을 찾아 롯데 자이언츠를 응원하며 목청껏 소리를 지르는 것으로 일주일의 스트레스를 한 번에 날려버립니다. 경기장에 직접 가지 못하는 날에는 TV 앞에 앉아 치킨을 뜯으며 선수들의 플레이 하나하나에 일희일비하는 열혈 팬입니다.
arts_persona                  : 김대훈 씨는 퇴근 후 방 안에 시티팝 음악을 크게 틀어놓고 멍하게 천장을 바라보며 상상의 나래를 펼치는 시간을 가장 아낍니다. 가끔은 부산 영도나 전포동의 작은 독립 서점을 돌아다니며 남들이 잘 모르는 작가의 시집을 찾아 읽는 정적인 취향을 가지고 있습니다.
travel_persona                : 김대훈 씨는 친구들과 함께 전국의 이름 없는 노포를 찾아다니며 투박한 시골 밥상과 제철 나물 정식을 맛보는 식도락 여행에 몰두합니다. 유명 관광지를 찍고 오는 여행 대신 숨겨진 맛집의 분위기와 그곳에서만 느낄 수 있는 정취를 기록하는 것에 큰 만족감을 느낍니다.
culinary_persona              : 김대훈 씨는 정갈한 나물 반찬이 나오는 한식당이나 분위기 좋은 동네 주점을 찾아 지인들과 술잔을 기울이는 시간을 즐깁니다. 배달 음식으로는 한 달에 한 번 정도만 기분 전환을 하며, 2주에 한 번은 반드시 직접 식당을 찾아가 공간이 주는 분위기를 함께 누립니다.
family_persona                : 김대훈 씨는 김해 내동의 자가 아파트에서 부모님을 모시고 살며 효심과 개인의 자유 사이에서 적절한 균형을 잡으려 노력하는 마흔 살 미혼 남성입니다. 부모님의 잔소리를 웃어넘기는 능글맞은 태도를 지녔지만, 집안일에는 다소 무심해 어머니의 꾸지람을 듣는 일이 잦습니다.
persona                       : 김대훈 씨는 김해에서 법률 사무원으로 근무하며 안정적인 삶을 영위하면서도, 예술적 감성과 식도락에 탐닉하는 낭만적인 40대 싱글 남성입니다.
cultural_background           : 김해 내동의 아파트에서 부모님을 모시고 살며, 지역 사회의 안정적인 분위기 속에서도 개인적인 자유분방함을 유지하며 살아갑니다. 전문대학 졸업 후 법률 사무직으로 빠르게 자리를 잡았지만, 가끔은 틀에 박힌 일상에서 벗어나 부산의 작은 독립 서점이나 전시회를 찾아다니며 새로운 자극을 얻습니다.
skills_and_expertise          : 복잡한 법원 제출 서류의 양식을 빠르게 파악해 처리하며, 의뢰인들이 느끼는 막연한 불안감을 특유의 능숙한 말솜씨로 다독여 원만한 합의를 이끌어냅니다. 규정의 빈틈을 찾아 더 효율적인 처리 방식을 제안하는 유연한 업무 감각이 뛰어납니다.
skills_and_expertise_list     : ['법률 문서 작성 및 관리', '의뢰인 응대 및 갈등 조율', '행정 절차 최적화', '사건 기록 데이터베이스 관리']
hobbies_and_interests         : 사직야구장에서 롯데 자이언츠 경기를 보며 목청껏 응원하는 것으로 스트레스를 풀고, 주말이면 친구들과 함께 전국의 노포를 찾아다니며 투박한 시골 밥상이나 제철 나물 정식을 즐깁니다. 집에서는 낮잠을 자거나 시티팝 음악을 크게 틀어놓고 멍하게 시간을 보내는 순간을 소중히 여깁니다.
hobbies_and_interests_list    : ['사직야구장 직관', '전국 노포 음식점 탐방', '시티팝 음악 감상', '뒷산 가벼운 등산', '동네 단골 술집에서의 한잔']
career_goals_and_ambitions    : 조직 내에서 단순히 지시를 따르는 직원이 아니라, 어떤 난처한 상황에서도 명쾌한 해결책을 제시하는 대체 불가능한 실무 전문가로 인정받고자 합니다. 현재의 안정적인 소득을 바탕으로 퇴근 후의 삶을 풍요롭게 가꾸며, 언젠가는 자신의 취향이 온전히 반영된 작은 작업실을 갖길 바랍니다.
sex                           : 남자
age                           : 40
marital_status                : 미혼
military_status               : 비현역
family_type                   : 부모와 동거
housing_type                  : 아파트
education_level               : 2~3년제 전문대학
bachelors_field               : 해당없음
occupation                    : 그 외 법률 관련 사무원
district                      : 경상남-김해시
province                      : 경상남
country                       : 대한민국
```

## `province` distribution

- distinct: **17**
```
province
경기     262154
서울     185228
부산      65285
경상남     62416
인천      58991
경상북     50298
대구      46934
충청남     41456
전라남     34391
전북      34188
충청북     31296
강원      30200
대전      28646
광주      27594
울산      21317
제주      12673
세종       6933
```

## sex × age-band marginals + proportional N=300 allocation

```
sex age_band  n_pop  pop_share  target_300  under_floor_25
 남자    19-29  76199   0.076199          23            True
 남자    30-44 124182   0.124182          37           False
 남자    45-59 143415   0.143415          43           False
 남자      60+ 151762   0.151762          46           False
 여자    19-29  69303   0.069303          21            True
 여자    30-44 114306   0.114306          34           False
 여자    45-59 142153   0.142153          43           False
 여자      60+ 178680   0.178680          54           False
```

- total target N before floor-adjust: **301**
- cells under floor of 25: **2**
- smallest target cell: **21**, largest: **54**

## done

