import streamlit as st
import random

# 단어 리스트
words = {
    'big': '큰',
    'bird': '새',
    'cute': '귀여운',
    'elephant': '코끼리',
    'giraffe': '기린',
    'lion': '사자',
    'small': '작은',
    'tall': '키 큰',
    'tiger': '호랑이',
    'zebra': '얼룩말'
}

# 퀴즈 타입 선택
quiz_type = st.radio("퀴즈 타입을 선택하세요:", ('영어 -> 한국어', '한국어 -> 영어'))

# 상태 초기화
if 'previous_word' not in st.session_state:
    st.session_state.previous_word = None
if 'previous_meaning' not in st.session_state:
    st.session_state.previous_meaning = None
if 'new_word' not in st.session_state:
    st.session_state.new_word, st.session_state.new_meaning = random.choice(list(words.items()))
if 'show_next' not in st.session_state:
    st.session_state.show_next = False

# 이전 단어와 의미 가져오기
word = st.session_state.new_word
meaning = st.session_state.new_meaning

# 정답과 오답 선택
options = [meaning] if quiz_type == '영어 -> 한국어' else [word]
while len(options) < 4:
    option = random.choice(list(words.values() if quiz_type == '영어 -> 한국어' else words.keys()))
    if option not in options:
        options.append(option)
random.shuffle(options)

if not st.session_state.show_next:
    if quiz_type == '영어 -> 한국어':
        st.write(f"영어 단어: {word}")
        answer = st.radio("정답을 선택하세요:", options)
        if st.button("제출"):
            if answer == meaning:
                st.success("정답입니다!")
            else:
                st.error(f"틀렸습니다. 정답은 {meaning}입니다.")
            st.session_state.show_next = True
    else:
        st.write(f"한국어 뜻: {meaning}")
        answer = st.radio("정답을 선택하세요:", options)
        if st.button("제출"):
            if answer == word:
                st.success("정답입니다!")
            else:
                st.error(f"틀렸습니다. 정답은 {word}입니다.")
            st.session_state.show_next = True
else:
    if st.button("다음 문제"):
        st.session_state.new_word, st.session_state.new_meaning = random.choice(list(words.items()))
        st.session_state.show_next = False
        st.experimental_rerun()
