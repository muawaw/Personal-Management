import streamlit as st
from pathlib import Path
import time

from frontend import main_dashboard_view
from backend import master_data

st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.components.v1.html(
    """
    <script>
    let idleTime = 0;
    const maxIdleTime = 15 * 60 * 1000; // 15 Minutes

    function resetTimer() {
        idleTime = 0;
    }

    // Reset idle timer on user interaction
    window.onload = resetTimer;
    window.onmousemove = resetTimer;
    window.onmousedown = resetTimer; 
    window.ontouchstart = resetTimer;
    window.onclick = resetTimer;
    window.onkeypress = resetTimer;

    setInterval(function() {
        idleTime += 1000;
        if (idleTime >= maxIdleTime) {
            // Stop WebSocket / freeze page to allow Render server to sleep
            window.stop();
        }
    }, 1000);
    </script>
    """,
    height=0,
)

def load_css(file_path: Path):
    """Utility to read a external CSS file and wrap it in a style tag."""
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
def warm_up_backend():
    """Perform real backend checks instead of a static timer."""
    # 1. Warm up DB connection / Test query
    try:
        master_data.get_all_categories()
    except Exception:
        pass

def show_boot_screen():
    """Displays a Discord-like boot screen when waking up from cold sleep."""
    loader_placeholder = st.empty()
    
    # Load external CSS file directly into Streamlit
    css_path = Path(__file__).parent / "loading_screen.css"
    load_css(css_path)
    
    with loader_placeholder.container():
        st.markdown(
            """
            <div class="discord-loader-container">
                <div class="discord-spinner"></div>
                <div class="discord-loader-title">Waking up server...</div>
                <div class="discord-loader-subtitle">Connecting to Personal Use Management System. Hang tight!</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Simulate / perform initial warm-up
        # time.sleep(2) 
        warm_up_backend()
        
    loader_placeholder.empty()

def init_app_lifecycle():
    """Handles cold boot state and automatic idle timeout reset."""
    if "is_server_woken" not in st.session_state:
        st.session_state.is_server_woken = True
        show_boot_screen()

    st.session_state.last_active_time = time.time()

init_app_lifecycle()

def main():
    pg = st.navigation(
        {
            "Overview": [main_dashboard_view.dashboard_page],
            "Operational Management": [main_dashboard_view.purchase_page, main_dashboard_view.sales_page],
            "Inventory Management": [main_dashboard_view.inventory_page, main_dashboard_view.stock_opname_page],
            "Configuration": [main_dashboard_view.master_data_page],
        }
    )
    pg.run()

if __name__ == "__main__":
    main()