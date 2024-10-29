import streamlit as st
from israel_trends import fetch_trends as fetch_israel_trends
from lebanon_trends import fetch_trends as fetch_lebanon_trends
from iran_trends import fetch_trends as fetch_iran_trends
from czech_trends import fetch_trends as fetch_czech_trends

def main():
    st.set_page_config(
        page_title="Trends to Stories",
        page_icon="📊",
        layout="wide"
    )

    st.title("🔍 Official News vs. Real Searches")
    st.markdown("### Revealing the Gap Between Headlines and Reality")

    # Country selector with flags
    country_options = {
        "Israel": ("IL", "🇮🇱", fetch_israel_trends),
        "Lebanon": ("LB", "🇱🇧", fetch_lebanon_trends),
        "Iran": ("IR", "🇮🇷", fetch_iran_trends),
        "Czech Republic": ("CZ", "🇨🇿", fetch_czech_trends)
    }

    # Create two columns for layout
    col1, col2 = st.columns([2, 3])

    with col1:
        country = st.selectbox(
            "Choose a country to analyze:",
            list(country_options.keys()),
            format_func=lambda x: f"{country_options[x][1]} {x}"
        )

        # Get country code and fetch function
        country_code, flag, fetch_function = country_options[country]
        
        if st.button(f"Analyze {flag} {country}", use_container_width=True):
            with st.spinner(f"Analyzing {country}..."):
                # Run the analysis
                try:
                    results = fetch_function()
                    
                    if results and 'trends_data' in results:
                        st.session_state.results = results
                        st.session_state.current_country = country
                        st.session_state.current_flag = flag
                        st.session_state.current_code = country_code
                    else:
                        st.error(f"No data found for {country}")
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    with col2:
        if 'results' in st.session_state and 'current_country' in st.session_state:
            results = st.session_state.results
            country = st.session_state.current_country
            flag = st.session_state.current_flag
            code = st.session_state.current_code
            
            # Create two columns for comparison
            news_col, trends_col = st.columns(2)
            
            with news_col:
                st.header("📰 Official Headlines")
                if 'headlines' in results and results['headlines']:
                    for headline in results['headlines']:
                        st.markdown(f"• {headline}")
                else:
                    st.info("No recent headlines found")
            
            with trends_col:
                st.header("🔍 What People Search For")
                for trend in results['trends_data']:
                    with st.expander(f"**{trend['title']}**", expanded=True):
                        if trend['related']:
                            st.markdown("Related searches:")
                            for related in trend['related']:
                                st.markdown(f"• {related}")
                        else:
                            st.info("No related searches found")
            
            # Show analysis if available
            if 'analysis' in results and results['analysis']:
                st.markdown("---")
                st.header("🎭 The Reality Behind the Headlines")
                st.markdown(results['analysis'])

    # Add navigation hint
    st.sidebar.markdown("→ View historical analyses in the Archive page")

if __name__ == "__main__":
    main()
