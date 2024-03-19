import streamlit as st

st.markdown(
    """
    <style>
    .stButton > button {
        width: 100%;
        height: auto;
    }
    
    /* Apply margin-top only for non-mobile views */
    @media (min-width: 768px) {
        [data-testid="stFormSubmitButton"] > button {
            margin-top: 28px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center;'>🤖 AI ThinkTank 🤖</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>1. Giới thiệu tổng quan</h2>", unsafe_allow_html=True)
st.sidebar.markdown("Trang chủ")
st.image("https://www.notion.so/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F0c6b2a24-183c-4a8c-889c-6d8d4d66a1d6%2F253fc070-879f-4742-92e4-f4d38784e619%2FUntitled.png?table=block&id=62902ffb-885f-49dc-8cb5-f885ada0fada&spaceId=0c6b2a24-183c-4a8c-889c-6d8d4d66a1d6&width=2000&userId=d6573d3c-3d81-4d95-81bc-512898e8b7a4&cache=v2", caption='AI ThinkTank', use_column_width=True)
st.write("""Sự bùng nổ của các mô hình ngôn ngữ lớn (LLM) mở ra những ứng dụng đột phá, góp phần nâng tầm hiệu quả công việc trong nhiều lĩnh vực, bao gồm cả tranh luận (hay còn gọi là debate). Nhờ khả năng tạo ra văn bản chất lượng cao, LLM hỗ trợ đắc lực cho việc xây dựng lập luận chặt chẽ, phân tích điểm mạnh, điểm yếu trong lập luận của đối phương, từ đó giúp người dùng luyện tập kỹ năng phản biện và nâng cao khả năng nhìn nhận đa chiều về một chủ đề. Nhận thức được tiềm năng to lớn của LLM trong lĩnh vực tranh luận, ứng dụng **AI ThinkTank** ra đời, hứa hẹn trở thành trợ thủ đắc lực hỗ trợ người dùng trong việc phát triển ý tưởng và trau dồi tư duy phản biện""")
st.write("""Ứng dụng được tạo nên bởi **Gemini Pro 1.0**, một mô hình ngôn ngữ tiên tiến do Google phát triển. **Gemini Pro 1.0** sở hữu khả năng xử lý ngôn ngữ tự nhiên vượt trội, cho phép nó hiểu và tạo ra văn bản một cách mượt mà, logic và đầy sáng tạo. Nhờ vậy, đồ án có thể hỗ trợ người dùng một cách hiệu quả trong việc xây dựng lập luận, phân tích thông tin và phát triển ý tưởng.""")
st.write("""Ứng dụng được lấy cảm hứng từ ứng dụng cùng tên do kỹ sư AI người đức David Satomi và các cộng sự thực hiện ở cuộc thi hakathon do lab.ai tổ chức. Người thực hiện chỉnh sửa và nâng cấp ứng dụng:""")

data = {
    "MSSV": ["20127258", "20127166"],
    "Họ và tên": ["Hoàng Phước Nguyên", "Nguyễn Huy Hoàn"]
}

st.table(data)


st.markdown("<h2 style='text-align: center;'>2. Tính năng AI ThinkTank</h2>", unsafe_allow_html=True)


