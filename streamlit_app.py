import streamlit as st
import json
import time
from typing import Any, Dict
import jwt

def json_create(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)

def build_canvas_header(
        client_id: str,
        private_key: str
) -> dict:

    if not client_id or not private_key:
        raise RuntimeError("Canvas credentials are missing")

    now = int(time.time())
    payload = {
        "iss": client_id,
        "sub": "canvas-app-user",
        "aud": "https://login.salesforce.com",
        "exp": now + 300,
    }

    signed_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    if isinstance(signed_jwt, bytes):
        signed_jwt = signed_jwt.decode("utf-8")

    return {"Authorization": f"Bearer {signed_jwt}"}

def send_to_canvas(
        payload: Dict[str, Any],
        client_id: str,
        private_key: str
) -> Dict[str, Any]:
    CANVAS_URL = "https://yourorg.my.salesforce.com/apex/CanvasEndpoint"

    headers = build_canvas_header(client_id, private_key)

    resp = requests.post(
        url=CANVAS_URL,
        json=payload,
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()

st.sidebar.header("Canvas Credentials")

client_id = st.sidebar.text_input(
    label="Canvas App Client‑ID",
    placeholder="",
    type="default"
)

private_key = st.sidebar.text_area(
    label="Canvas App Private‑Key",
    placeholder="",
    height=200
)

def main() -> None:
    st.set_page_config(page_title="Salesforce Canvas JSON Tester", layout="wide")

    st.title("Salesforce Canvas JSON Tester")

    json_input = st.text_area(
        label="JSON payload",
        value='',
        height=350,
        placeholder='',
    )

    try:
        payload = json.loads(json_input)
        json_valid = True
    except json.JSONDecodeError as err:
        payload = None
        json_valid = False
        st.error(f"Invalid JSON: {err}")

    if st.button("Send to Canvas") and json_valid:
        if not client_id or not private_key:
            st.error("Creds are missing")
            return

        with st.spinner("Sending…"):
            try:
                response = send_to_canvas(payload, client_id, private_key)
            except requests.HTTPError as http_err:
                st.error(f"HTTP error: {http_err}\n{http_err.response.text}")
                return
            except Exception as exc:
                st.error(f"{exc}")
                return

        st.success("Request completed")
        st.subheader("Payload Sent")
        st.code(json_create(payload), language="json")
        st.subheader("Response")
        st.code(json_create(response), language="json")

if __name__ == "__main__":
    main()
