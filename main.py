import streamlit as st
import uuid
from dotenv import load_dotenv
import os

from model import Event, Attendee

# streamlit의 session에 database로 출석 데이터들을 관리
# 확장한다면 실제 인메모리에서 관리하지 않고 DB를 별도로 파서 관리 가능
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
                st.session_state.DATABASE[new_event_id] = Event(
                    name=event_name,
                    password=password,
                )
                st.success(f"이벤트 '{event_name}' 생성 완료!")
            else:
                st.error("이벤트 이름과 비밀번호를 모두 입력하세요.")

    if st.session_state.DATABASE:
        st.subheader("생성된 이벤트 목록")
        st.write(f"총 **{len(st.session_state.DATABASE)}개**의 이벤트가 있습니다.")

        for eid, event in st.session_state.DATABASE.items():
            attendee_count = event.attendees_count()

            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"이벤트 : **{event.name}**")
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
                    preview_attendees = event.preview_attendees()
                    preview_names = [f"{attendee.name}({attendee.student_id})" for attendee in preview_attendees]
                    preview_text = ", ".join(preview_names)
                    if attendee_count > 3:
                        preview_text += f" 외 {attendee_count - 3}명"
                    st.caption(f"{preview_text}")
                else:
                    st.caption("아직 출석한 학생이 없습니다.")

                st.divider()
    else:
        st.info("아직 생성된 이벤트가 없습니다. 위에서 새 이벤트를 만들어보세요.")

elif page == "event" and event_id:
    event = st.session_state.DATABASE.get(event_id)

    if event is None:
        st.error("존재하지 않는 이벤트입니다.")
        if st.button("홈으로 돌아가기"):
            st.query_params.clear()
            st.rerun()
    else:
        st.title(f"출석 체크 - {event.name}")

        with st.form("attendance"):
            input_password = st.text_input("출석 비밀번호(이벤트 생성자에게 안내받으세요)", type="password")
            name = st.text_input("이름")
            student_id = st.text_input("학번")
            submitted = st.form_submit_button("출석하기")

            if submitted:
                if not event.check_password(input_password):
                    st.error("비밀번호가 틀렸습니다.")
                elif not name or not student_id:
                    st.error("이름과 학번을 모두 입력하세요.")
                else:
                    if event.already_attended(student_id):
                        st.warning(f"학번 {student_id}는 이미 출석했습니다.")
                    else:
                        attendee = Attendee(name=name, student_id=student_id)
                        event.attend(attendee)
                        st.success(f"{name}({student_id}) 출석 완료!")

        st.subheader("현재 출석 명단")
        if event.is_blank():
            st.info("아직 출석한 사람이 없습니다.")
        else:
            st.write(f"**총 {event.attendees_count()}명 출석**")
            for index, attendee in enumerate(event.all_attendees(), 1):
                st.text(f"{index:2d}. {attendee.student_id} - {attendee.name}")

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
        st.title(f"출석 명단 조회 - {event.name}")

        if not event.is_blank():
            st.success(f"**총 {event.attendees_count()}명 출석**")

            st.subheader("출석자 명단")
            for index, attendee in enumerate(event.all_attendees(), 1):
                col1, col2, col3 = st.columns([1, 2, 2])
                with col1:
                    st.write(f"{index}")
                with col2:
                    st.write(f"{attendee.student_id}")
                with col3:
                    st.write(f"{attendee.name}")
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
