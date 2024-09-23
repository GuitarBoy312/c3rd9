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

# 랜덤 단어 선택
word, meaning = random.choice(list(words.items()))

if quiz_type == '영어 -> 한국어':
    st.write(f"영어 단어: {word}")
    answer = st.text_input("한국어 뜻을 입력하세요:")
    if st.button("제출"):
        if answer == meaning:
            st.success("정답입니다!")
        else:
            st.error(f"틀렸습니다. 정답은 {meaning}입니다.")
else:
    st.write(f"한국어 뜻: {meaning}")
    answer = st.text_input("영어 단어를 입력하세요:")
    if st.button("제출"):
        if answer == word:
            st.success("정답입니다!")
        else:
            st.error(f"틀렸습니다. 정답은 {word}입니다.")
