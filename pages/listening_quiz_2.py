import streamlit as st
from openai import OpenAI
import random
import base64
import re

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])

def generate_question():
    question_format = random.choice(["이 동물의 모습은 어떤가요?", "어떤 동물에 대해 이야기 했나요?"])
    key_expression = f"""
❶ A: Look at the bird.🐤 - B: It’s small.
❷ A: Look at the lion.🦁 - B: It’s big.
❸ A: Look at the tiger.🐅 - B: It’s small.
❹ A: Look at the elephant.🐘 - B: It’s big.
❺ A: Look at the zebra.🦓 - B: It’s cute.
❻ A: Look at the giraffe.🦒 - B: It’s tall.
"""
    prompt = f"""{key_expression}의 대화 중 하나를 읽어주세요. 
    그 후 대화 내용에 관한 객관식 질문을 한국어로 만들어주세요.  
    조건: 문제의 정답은 1개입니다.  


    [한국어 질문]
    조건: {question_format}을 만들어야 합니다.
    질문: (한국어로 된 질문) 이 때, 선택지는 한국어로 제공됩니다.
    A. (선택지)
    B. (선택지)
    C. (선택지)
    D. (선택지)
    정답: (정답 선택지)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def split_dialogue(text):
    lines = text.strip().split('\n')
    speakers = {}
    for line in lines:
        match = re.match(r'([A-Z]):\s*(.*)', line)
        if match:
            speaker, content = match.groups()
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(content)
    return speakers

def text_to_speech(text, voice):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        audio_bytes = response.content
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_tag = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        
        return audio_tag
    except Exception as e:
        st.error(f"음성 생성에 실패했습니다: {e}")
        return ""

def generate_dialogue_audio(dialogue):
    speakers = split_dialogue(dialogue)
    audio_tags = []
    
    for speaker, lines in speakers.items():
        text = " ".join(lines)
        voice = "alloy" if speaker == "A" else "nova"  # A는 여성 목소리, B는 남성 목소리
        audio_tag = text_to_speech(text, voice)
        if audio_tag:
            audio_tags.append(audio_tag)
    
    return "".join(audio_tags)

def generate_explanation(question, correct_answer, user_answer, dialogue):
    prompt = f"""
    다음 영어 대화와 관련된 질문에 대해 학생이 오답을 선택했습니다. 
    대화: {dialogue}
    질문: {question}
    정답: {correct_answer}
    학생의 답변: {user_answer}
    
    이 학생에게 왜 그들의 답변이 틀렸는지, 그리고 정답이 무엇인지 설명해주세요. 
    설명은 친절하고 격려하는 톤으로 작성해주세요. 
    대화의 내용을 참조하여 구체적으로 설명해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어 퀴즈 선생님 퀴즐링🕵️‍♂️")
st.subheader("❓동물의 크기와 모습에 관한 퀴즈")
st.divider()

#확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [새 문제 만들기] 버튼을 눌러 문제 만들기.<br>
    2️⃣ 재생 막대의 ▶ 버튼을 누르고 대화를 들어보기.<br>
    재생 막대의 오른쪽 스노우맨 버튼(점 세개)을 눌러 재생 속도를 조절할 수 있습니다.<br> 
    3️⃣ 정답을 선택하고 [정답 확인] 버튼 누르기.<br>
    4️⃣ 정답과 대화 스크립트 확인하기.<br>
    <br>
    🙏 퀴즐링은 완벽하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [새 문제 만들기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)

# 세션 상태 초기화
if 'question_generated' not in st.session_state:
    st.session_state.question_generated = False

if st.button("새 문제 만들기"):
    # 세션 상태 초기화
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    full_content = generate_question()
    
    if "[한국어 질문]" in full_content:
        dialogue, question_part = full_content.split("[한국어 질문]")
        
        question_lines = question_part.strip().split("\n")
        question = question_lines[0].replace("질문:", "").strip() if question_lines else ""
        options = question_lines[1:5] if len(question_lines) > 1 else []
        correct_answer = ""
        
        for line in question_lines:
            if line.startswith("정답:"):
                correct_answer = line.replace("정답:", "").strip()
                break
        
        st.session_state.question = question
        st.session_state.dialogue = dialogue.strip()
        st.session_state.options = options
        st.session_state.correct_answer = correct_answer
        st.session_state.question_generated = True
        
        # 새 대화에 대한 음성 생성 (남녀 목소리 구분)
        st.session_state.audio_tags = generate_dialogue_audio(st.session_state.dialogue)
        
        # 페이지 새로고침
        st.rerun()
    else:
        st.error("질문 생성에 실패했습니다. 다시 시도해주세요.")

if 'question_generated' in st.session_state and st.session_state.question_generated:
    st.markdown("### 질문")
    st.write(st.session_state.question)
    
    # 저장된 음성 태그 사용
    st.markdown("### 대화 듣기")
    st.write("왼쪽부터 순서대로 들어보세요. 너무 빠르면 눈사람 버튼을 눌러 속도를 조절해보세요.")
    st.markdown(st.session_state.audio_tags, unsafe_allow_html=True)
    
    with st.form(key='answer_form'):
        selected_option = st.radio("정답을 선택하세요:", st.session_state.options, index=None)
        submit_button = st.form_submit_button(label='정답 확인')
        
        if submit_button:
            if selected_option:
                st.info(f"선택한 답: {selected_option}")
                if selected_option.strip() == st.session_state.correct_answer.strip():  
                    st.success("정답입니다!")
                    st.text(st.session_state.dialogue)
                else:
                    st.error(f"틀렸습니다. 정답은 {st.session_state.correct_answer}입니다.")
                    st.text(st.session_state.dialogue)
                    
                    # 오답 설명 생성
                    explanation = generate_explanation(
                        st.session_state.question,
                        st.session_state.correct_answer,
                        selected_option,
                        st.session_state.dialogue
                    )
                    st.markdown("### 오답 설명")
                    st.write(explanation)
            else:
                st.warning("답을 선택해주세요.")
