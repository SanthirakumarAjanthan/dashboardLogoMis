import streamlit as st

# Set the page configuration
st.set_page_config(
    page_title="Software Engineer Portfolio",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main-header { font-size: 3em; font-weight: bold; margin-bottom: 10px; }
    .sub-header { font-size: 1.5em; margin-bottom: 5px; color: #6c757d; }
    .project-box { padding: 15px; border: 1px solid #ddd; margin-bottom: 15px; border-radius: 5px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Navigation Bar
st.markdown(
    """
    <nav style="background-color:#f8f9fa; padding: 10px;">
        <a style="margin-right: 20px; font-weight:bold;" href="#home">Home</a>
        <a style="margin-right: 20px; font-weight:bold;" href="#skills">Skills</a>
        <a style="margin-right: 20px; font-weight:bold;" href="#projects">Projects</a>
        <a style="margin-right: 20px; font-weight:bold;" href="#contact">Contact</a>
    </nav>
    """,
    unsafe_allow_html=True,
)

# Home Section
st.markdown('<h1 class="main-header" id="home">Welcome to My Portfolio</h1>', unsafe_allow_html=True)
st.image("https://via.placeholder.com/800x200.png", caption="Hi, I'm [Your Name], a Software Engineer.")

# About Me
st.markdown('<p class="sub-header">About Me</p>', unsafe_allow_html=True)
st.write(
    "I’m a software engineer specializing in building high-quality web and mobile applications. "
    "I have a passion for learning new technologies and solving challenging problems."
)

# Skills Section
st.markdown('<h2 class="main-header" id="skills">Skills</h2>', unsafe_allow_html=True)
cols = st.columns(3)
skills = ["Python", "JavaScript", "React", "Django", "Streamlit", "SQL", "Machine Learning"]
for idx, skill in enumerate(skills):
    with cols[idx % 3]:
        st.markdown(f"<li>{skill}</li>", unsafe_allow_html=True)

# Projects Section
st.markdown('<h2 class="main-header" id="projects">Projects</h2>', unsafe_allow_html=True)

# Sample Project 1
st.markdown('<div class="project-box">', unsafe_allow_html=True)
st.markdown('<b>Project 1: Portfolio Website</b>', unsafe_allow_html=True)
st.write(
    "A responsive portfolio website built using Streamlit. It showcases my skills, projects, and contact information."
)
st.image("https://via.placeholder.com/400x200.png", caption="Portfolio Website Screenshot")
st.markdown("</div>", unsafe_allow_html=True)

# Add more projects as needed...

# Contact Section
st.markdown('<h2 class="main-header" id="contact">Contact</h2>', unsafe_allow_html=True)
st.write("Feel free to reach out to me:")
st.write("- **Email**: [your.email@example.com](mailto:your.email@example.com)")
st.write("- **LinkedIn**: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)")
st.write("- **GitHub**: [github.com/yourusername](https://github.com/yourusername)")
