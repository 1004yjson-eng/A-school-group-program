import streamlit as st
import random
import pandas as pd
import io

# --- Streamlit 앱 설정 ---
st.set_page_config(page_title="모둠 자동 편성기", layout="centered")

# 사용자 지정 CSS (미관 개선)
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        color: #1E88E5; /* Google Blue */
        text-align: center;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .group-output {
        border: 1px solid #ddd;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    .footer {
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid #eee;
        text-align: center;
        font-size: 0.8em;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


# --- 제목 및 설명 ---
st.markdown('<p class="big-font">👨‍👩‍👧‍👦 모둠 자동 편성 프로그램</p>', unsafe_allow_html=True)
st.write("학생 명단을 입력하고 기준을 설정하면, 자동으로 공평하게 모둠을 편성해 줍니다.")
st.caption("결과가 마음에 들지 않으면 '다시 편성하기' 버튼을 누르세요.")


# --- 학생 명단 입력 섹션 ---
st.subheader("1. 학생 명단 입력 (택 1)")

students_text = st.text_area(
    "학생 이름 목록을 줄바꿈(엔터)으로 구분하여 입력해주세요.",
    "김민준\n이서윤\n박도현\n정하윤\n최지호\n조서연\n윤준서\n장지우\n임시우\n한예나\n배시현\n황은서",
    height=200
)

uploaded_file = st.file_uploader("또는, 학생 이름이 포함된 CSV 파일을 업로드하세요 (첫 번째 열만 사용).", type=['csv'])


# --- 모둠 편성 기준 설정 섹션 ---
st.subheader("2. 모둠 편성 기준 설정")
col1, col2 = st.columns(2)

grouping_option = col1.radio(
    "편성 기준을 선택하세요:",
    ('모둠당 인원수', '만들 모둠 개수')
)

target_value = col2.number_input(
    "기준 값 입력:",
    min_value=1,
    value=4,
    step=1,
    help=f"선택한 기준에 따라 {grouping_option}을 설정합니다."
)

# --- 메인 편성 로직 함수 ---
def perform_group_assignment(student_list, option, value):
    """학생 리스트와 기준에 따라 모둠을 편성하는 함수"""
    if not student_list:
        return []

    random.shuffle(student_list)
    groups = []
    num_students = len(student_list)

    if option == '모둠당 인원수':
        group_size = value
        num_groups = (num_students + group_size - 1) // group_size
    else: # '만들 모둠 개수'
        num_groups = value
        if num_groups == 0:
            return []
        group_size = num_students // num_groups

    # 초기 모둠 리스트 생성
    groups = [[] for _ in range(num_groups)]

    # 학생들을 균등하게 분배
    for i, student in enumerate(student_list):
        group_index = i % num_groups
        groups[group_index].append(student)

    # 1명도 편성되지 않은 빈 그룹 제거 (이론상 일어나기 어렵지만 안전장치)
    groups = [g for g in groups if g]
    
    return groups

# --- 결과 출력 섹션 ---
st.subheader("3. 결과 확인")

# '다시 편성하기' 버튼
if st.button("✨ 모둠 편성 시작 / 다시 편성하기", type="primary"):
    
    # 1. 학생 명단 준비
    students = []
    
    if uploaded_file is not None:
        try:
            # CSV 파일 읽기
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            if df.empty:
                 st.error("업로드된 파일에 데이터가 없습니다. 이름을 입력하거나 다른 파일을 사용해주세요.")
            else:
                # 첫 번째 열의 값들을 학생 이름으로 사용
                students = df.iloc[:, 0].astype(str).tolist()
        except Exception as e:
            # 인코딩 문제 등을 처리
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            st.warning("CSV 파일의 인코딩이 'utf-8'인지 확인해 주세요.")
            
    # 파일이 없거나, 파일 읽기에 실패했을 경우 텍스트 영역 사용
    if not students and students_text:
        students = [name.strip() for name in students_text.split('\n') if name.strip()]

    # 최종 유효 학생 수 체크
    if not students:
        st.warning("편성할 학생 이름이 없습니다. 명단을 입력하거나 파일을 업로드해주세요.")
    elif target_value <= 0:
        st.error("모둠 편성 기준 값은 1 이상이어야 합니다.")
    else:
        # 2. 편성 실행
        with st.spinner('모둠을 편성하는 중...'):
            final_groups = perform_group_assignment(students, grouping_option, target_value)
        
        # 3. 결과 표시
        if final_groups:
            st.success(f"✅ 총 {len(final_groups)}개의 모둠이 성공적으로 편성되었습니다!")

            for i, group in enumerate(final_groups):
                st.markdown(
                    f'<div class="group-output"><strong>{i+1}조</strong> ({len(group)}명): {", ".join(group)}</div>',
                    unsafe_allow_html=True
                )
        else:
             st.warning("편성 가능한 그룹을 만들 수 없습니다. 기준 값을 다시 확인해 주세요.")

# --- Streamlit Cloud 배포 안내 ---
st.markdown('<div class="footer">이 프로그램은 Python Streamlit을 사용하여 개발되었습니다.</div>', unsafe_allow_html=True)
