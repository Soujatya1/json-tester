import streamlit as st
import json

st.set_page_config(page_title="Streamlit ↔ Salesforce Canvas", layout="wide")

with open("canvas.html", "r", encoding="utf-8") as f:
    canvas_html = f.read()

def handle_canvas_msg(msg):
    channel = msg.get("channel")
    payload = msg.get("payload")
    if channel == "to-streamlit":
        st.session_state["salesforce_response"] = payload
        st.experimental_rerun()

st.components.v1.html(
    canvas_html,
    height=500,
    width="100%",
    scrolling=True,
    # key="canvas_app",
    #on_message=handle_canvas_msg
)

if "salesforce_response" in st.session_state:
    st.success("Received response from Salesforce Canvas")
    st.json(st.session_state["salesforce_response"])
else:
    st.info("⏳ Waiting for a response…")

st.markdown("---")
st.subheader("Send a JSON payload to the Canvas app")

json_input = st.text_area(
    label="Paste your JSON payload here",
    height=200,
    placeholder=""
)

if st.button("Send JSON"):
    try:
        payload = json.loads(json_input or "{}")
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
        payload = None

    if payload is not None:
        st.components.v1.html(
            "",
            height=0,
            width=0,
            js=f"""
              (function() {{
                var iframe = document.querySelector('#canvas_app iframe');
                if (!iframe) {{
                  console.error("Canvas iframe not found");
                  return;
                }}
                iframe.contentWindow.postMessage(
                  {{
                    channel: "from-streamlit",
                    payload: {json.dumps(payload)}
                  }},
                  "*"
                );
              }})();
            """
        )
        st.success("✅ Sent JSON to Canvas")
