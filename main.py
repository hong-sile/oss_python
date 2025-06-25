import streamlit as st
import uuid
from dotenv import load_dotenv
import os

# streamlit의 session에 database로 출석 데이터들을 관리
if 'DATABASE' not in st.session_state:
    st.session_state.DATABASE = {}

load_dotenv()

query_params = st.query_params
page = query_params.get("page", "home")
event_id = query_params.get("event_id", None)
main_url = os.getenv('MAIN_URL')

# 메인 페이지이고, 출석이벤트를 생성하거나 간단하게 이미 있는 출석 이벤트들을 조회할 수 있습니다.
if page == "home":
    st.title("출석 이벤트 생성")

    with st.form("create_event"):
        event_name = st.text_input("이벤트 이름")
        password = st.text_input("고유한 출석 비밀번호 (출석할 때 입력해야하는 비밀번호입니다.)", type="password")
        submitted = st.form_submit_button("이벤트 생성")

        if submitted:
            if event_name and password:
                new_event_id = str(uuid.uuid4())
                st.session_state.DATABASE[new_event_id] = {
                    "event_name": event_name,
                    "password": password,
                    "attendees": []
                }
                st.success(f"이벤트 '{event_name}' 생성 완료!")

                st.markdown(f"""
                ### 생성된 링크들:
                - **출석 URL**: `{main_url}?page=event&event_id={new_event_id}`
                - **명단 조회 URL**: `{main_url}?page=view&event_id={new_event_id}`
                """)

                st.info("위 링크들을 복사해서 학생들에게 공유하세요!")
            else:
                st.error("이벤트 이름과 비밀번호를 모두 입력하세요.")

    if st.session_state.DATABASE:
        st.subheader("생성된 이벤트 목록")
        st.write(f"총 **{len(st.session_state.DATABASE)}개**의 이벤트가 있습니다.")

        for eid, event_data in st.session_state.DATABASE.items():
            attendee_count = len(event_data['attendees'])

            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"이벤트 : **{event_data['event_name']}**")
                    st.caption(f"출석자: {attendee_count}명")

                with col2:
                    if st.button("출석", key=f"attend_{eid}"):
                        st.query_params.page = "event"
                        st.query_params.event_id = eid
                        st.rerun()

                with col3:
                    if st.button("명단", key=f"view_{eid}"):
                        st.query_params.page = "view"
                        st.query_params.event_id = eid
                        st.rerun()

                if attendee_count > 0:
                    preview_attendees = event_data['attendees'][:3]
                    preview_names = [f"{a['name']}({a['student_id']})" for a in preview_attendees]
                    preview_text = ", ".join(preview_names)
                    if attendee_count > 3:
                        preview_text += f" 외 {attendee_count - 3}명"
                    st.caption(f"📝 {preview_text}")
                else:
                    st.caption("아직 출석자가 없습니다.")

                st.divider()
    else:
        st.info("아직 생성된 이벤트가 없습니다. 위에서 새 이벤트를 만들어보세요!")

elif page == "event" and event_id:
    event = st.session_state.DATABASE.get(event_id)

    if event is None:
        st.error("존재하지 않는 이벤트입니다.")
        if st.button("홈으로 돌아가기"):
            st.query_params.clear()
            st.rerun()
    else:
        st.title(f"출석 체크 - {event['event_name']}")

        with st.form("attendance"):
            input_password = st.text_input("출석 비밀번호", type="password")
            name = st.text_input("이름")
            student_id = st.text_input("학번")
            submitted = st.form_submit_button("출석하기")

            if submitted:
                if input_password != event["password"]:
                    st.error("비밀번호가 틀렸습니다.")
                elif not name or not student_id:
                    st.error("이름과 학번을 모두 입력하세요.")
                else:
                    existing_student = None
                    for attendee in event["attendees"]:
                        if attendee["student_id"] == student_id:
                            existing_student = attendee
                            break

                    if existing_student:
                        st.warning(f"학번 {student_id}는 이미 출석했습니다. (이름: {existing_student['name']})")
                    else:
                        attendee = {"name": name, "student_id": student_id}
                        event["attendees"].append(attendee)
                        st.success(f"{name}({student_id}) 출석 완료!")

        st.subheader("현재 출석 명단")
        if event["attendees"]:
            st.write(f"**총 {len(event['attendees'])}명 출석**")
            for i, a in enumerate(event["attendees"], 1):
                st.text(f"{i:2d}. {a['student_id']} - {a['name']}")
        else:
            st.info("아직 출석한 사람이 없습니다.")

        if st.button("홈으로 돌아가기"):
            st.query_params.clear()
            st.rerun()

elif page == "view" and event_id:
    event = st.session_state.DATABASE.get(event_id)

    if event is None:
        st.error("존재하지 않는 이벤트입니다.")
        if st.button("홈으로 돌아가기"):
            st.query_params.clear()
            st.rerun()
    else:
        st.title(f"출석 명단 조회 - {event['event_name']}")

        if event["attendees"]:
            st.success(f"**총 {len(event['attendees'])}명 출석**")

            # 테이블 형태로 표시
            st.subheader("출석자 명단")
            for i, a in enumerate(event["attendees"], 1):
                col1, col2, col3 = st.columns([1, 2, 2])
                with col1:
                    st.write(f"{i}")
                with col2:
                    st.write(f"{a['student_id']}")
                with col3:
                    st.write(f"{a['name']}")
        else:
            st.info("아직 출석한 사람이 없습니다.")

        if st.button("홈으로 돌아가기"):
            st.query_params.clear()
            st.rerun()
else:
    st.error("잘못된 접근입니다.")
    if st.button("홈으로 돌아가기"):
        st.query_params.clear()
        st.rerun()
