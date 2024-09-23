import streamlit as st
from openai import OpenAI
import os
import re
import random

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generate_question():
    words = {
        "big": "큰",
        "bird": "새",
        "cute": "귀여운",
        "elephant": "코끼리",
        "giraffe": "기린",
        "lion": "사자",
        "small": "작은",
        "tall": "키 큰",
        "tiger": "호랑이",
        "zebra": "얼룩말"
    }
    
    word, meaning = random.choice(list(words.items()))
    if random.choice([True, False]):
        question = f"'{word}'의 한국어 뜻은 무엇인가요?"
        correct_answer = meaning
        options = random.sample(list(words.values()), 3)
        if correct_answer not in options:
            options.append(correct_answer)
    else:
        question = f"'{meaning}'의 영어 단어는 무엇인가요?"
        correct_answer = word
        options = random.sample(list(words.keys()), 3)
        if correct_answer not in options:
            options.append(correct_answer)

    random.shuffle(options)
    prompt = f"""
    질문: {question}
    선택지:
    1. {options[0]}
    2. {options[1]}
    3. {options[2]}
    4. {options[3]}
    정답: {options.index(correct_answer) + 1}
    """
    return prompt

def parse_question_data(data):
    lines = data.split('\n')
    question = ""
    options = []
    correct_answer = None

    for line in lines:
        if line.startswith("질문:"):
            question = line.replace("질문:", "").strip()
        elif re.match(r'^\d+\.', line):
            options.append(line.strip())
        elif line.startswith("정답:"):
            correct_answer = line.replace("정답:", "").strip()

    # 정답을 숫자로 변환
    if correct_answer:
        correct_answer = int(re.search(r'\d+', correct_answer).group())

    return question, options, correct_answer

def explain_wrong_answer(question, user_answer, correct_answer):
    prompt = f"""
    질문: {question}
    사용자의 답변: {user_answer}
    정답: {correct_answer}

    위 정보를 바탕으로, 사용자가 왜 틀렸는지 간단히 설명해주세요. 그리고 정답이 왜 맞는지도 설명해주세요.
    답변은 한국어로 작성해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def main():
    # Streamlit UI

    # 메인 화면 구성
    st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링🕵️‍♂️")
    st.markdown("**❓어제 한 일에 대한 문장 읽기 퀴즈**")
    st.divider()

    #확장 설명
    with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
        st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 질문과 대화를 읽어보기<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

    # 세션 상태 초기화
    if 'question_data' not in st.session_state:
        st.session_state.question_data = None
        st.session_state.selected_option = None
        st.session_state.show_answer = False

    if st.button("새로운 문제 생성"):
        st.session_state.question_data = generate_question()
        st.session_state.selected_option = None
        st.session_state.show_answer = False

    if st.session_state.question_data:
        # 문제 데이터 파싱
        question, options, correct_answer = parse_question_data(st.session_state.question_data)

        st.subheader("질문")
        st.write(question)

        st.divider()
        st.write(passage)

        
        st.subheader("다음 중 알맞은 답을 골라보세요.")
        for i, option in enumerate(options, 1):
            if st.checkbox(option, key=f"option_{i}", value=st.session_state.selected_option == i):
                st.session_state.selected_option = i

        if st.button("정답 확인"):
            st.session_state.show_answer = True

        if st.session_state.show_answer:
            if st.session_state.selected_option is not None:
                if st.session_state.selected_option == correct_answer:
                    st.success("정답입니다!")
                else:
                    st.error(f"틀렸습니다. 정답은 {correct_answer}번입니다.")
                    explanation = explain_wrong_answer(
                        question, 
                        options[st.session_state.selected_option - 1], 
                        options[correct_answer - 1]
                    )
                    st.write("오답 설명:", explanation)
            else:
                st.warning("선택지를 선택해주세요.")

if __name__ == "__main__":
    main()
