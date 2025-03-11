import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import preprocessor
import helper

# Function to load the custom CSS
def load_css():
    with open("APP/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS
load_css()

# Sidebar customizations
st.sidebar.title("Whatsapp Chat Analyzer")
st.sidebar.markdown("<h3 style='text-align: center;'>Choose a file</h3>", unsafe_allow_html=True)

# File upload
uploaded_file = st.sidebar.file_uploader("Upload a WhatsApp chat file", type=["txt"])

if uploaded_file is not None:
    # Read file as bytes and preprocess
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # Convert 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Get the minimum and maximum date from the dataset
    min_date = df['date'].min()
    max_date = df['date'].max()

    # Display available date range for user information
    st.sidebar.subheader("Available Date Range")
    st.sidebar.write(f"Start Date: {min_date.strftime('%Y-%m-%d')}")
    st.sidebar.write(f"End Date: {max_date.strftime('%Y-%m-%d')}")

    # Date input selection (start and end date)
    start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.sidebar.date_input("End Date", min_value=start_date, max_value=max_date, value=max_date)

    # Show selected date range for user's reference
    st.sidebar.write(f"Selected Date Range: {start_date} to {end_date}")

    # Adjust start and end date if no data available for the selected date range
    if start_date > end_date:
        st.sidebar.error("End Date cannot be earlier than Start Date.")
    else:
        # Filter the DataFrame based on selected date range
        filtered_df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

        # If no data is available for the selected date range, adjust to nearest available date
        if filtered_df.empty:
            st.sidebar.warning("No data available for the selected date range. Adjusting to the nearest available date.")
            nearest_start = df[df['date'] >= pd.to_datetime(start_date)].head(1)['date'].min()
            nearest_end = df[df['date'] <= pd.to_datetime(end_date)].tail(1)['date'].max()

            # Update start and end dates if nearest dates are found
            if pd.notna(nearest_start):
                start_date = nearest_start
            if pd.notna(nearest_end):
                end_date = nearest_end

            filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            st.sidebar.success(f"Displaying data from {start_date} to {end_date}")

        # Proceed with the analysis if data is available
        if not filtered_df.empty:
            # Sidebar user selection
            user_list = filtered_df['user_name'].unique().tolist()
            user_list.remove("Group Notification")
            user_list.sort()
            user_list.insert(0, "Overall")

            selected_user = st.sidebar.selectbox("Show Analysis WRT", user_list)

            if st.sidebar.button("Show Analysis"):
                num_msg, num_words, num_media, num_links, num_time = helper.fetchStarts(selected_user, filtered_df)

                # Top Statistics Section
                st.markdown("<div class='title'>Top Statistics</div>", unsafe_allow_html=True)
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric(label="Total Messages", value=num_msg)

                with col2:
                    st.metric(label="Total Words", value=num_words)

                with col3:
                    st.metric(label="Total Media", value=num_media)

                with col4:
                    st.metric(label="Total Links", value=num_links)

                with col5:
                    st.metric(label="Active Days", value=num_time)

                # Monthly Analysis
                st.markdown("<div class='section-title'>Monthly Time Line</div>", unsafe_allow_html=True)
                time_line = helper.mothly_time_line(selected_user, filtered_df)

                fig, ax = plt.subplots()
                ax.plot(time_line["time"], time_line["msg"], color="red")
                plt.xticks(rotation=90)
                st.pyplot(fig)

                # Weekly Activity Map
                st.markdown("<div class='section-title'>Weekly Activity Map</div>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)

                weekly_activity = helper.week_activity_map(selected_user, filtered_df)

                with col1:
                    st.markdown("<div class='subsection-title'>Most Busy Day</div>", unsafe_allow_html=True)
                    fig, ax = plt.subplots()
                    ax.bar(weekly_activity.index, weekly_activity.values, color="orange")
                    plt.xticks(rotation=90)
                    st.pyplot(fig)

                # Monthly Activity Map
                monthly_activity = helper.monthly_activity_map(selected_user, filtered_df)

                with col2:
                    st.markdown("<div class='subsection-title'>Most Busy Month</div>", unsafe_allow_html=True)
                    fig, ax = plt.subplots()
                    ax.bar(monthly_activity.index, monthly_activity.values, color="purple")
                    plt.xticks(rotation=90)
                    st.pyplot(fig)

                # Heat Map
                st.markdown("<div class='section-title'>Weekly Activity Heat Map</div>", unsafe_allow_html=True)
                pivot_table = helper.activity_heatmap(selected_user, filtered_df)

                fig, ax = plt.subplots()
                ax = sns.heatmap(pivot_table, fmt='g')
                plt.yticks(rotation='horizontal')
                st.pyplot(fig)

                # Busiest Users in the Group (Group Level)
                if selected_user == "Overall":
                    st.markdown("<div class='section-title'>Most Busy Users</div>", unsafe_allow_html=True)
                    X, new_df = helper.fetchMostBusyUsers(filtered_df)

                    col1, col2 = st.columns(2)

                    with col1:
                        fig, ax = plt.subplots()
                        ax.bar(X.index, X.values, color="green")
                        plt.xticks(rotation=90)
                        st.pyplot(fig)

                    with col2:
                        st.dataframe(new_df.style.set_properties(**{'background-color': 'lightblue'}))

                # WordCloud
                st.markdown("<div class='section-title'>WordCloud</div>", unsafe_allow_html=True)
                df_wc = helper.createWordCloud(selected_user, filtered_df)

                fig, ax = plt.subplots()
                ax.imshow(df_wc)
                st.pyplot(fig)

                # Most Common Words
                st.markdown("<div class='section-title'>Most Common Words</div>", unsafe_allow_html=True)
                most_common_df = helper.most_common_words(selected_user, filtered_df)

                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1])
                plt.xticks(rotation=90)
                st.pyplot(fig)

                # Emoji Analysis
                st.markdown("<div class='section-title'>Emoji Analysis</div>", unsafe_allow_html=True)
                emoji_df = helper.emoji_helper(selected_user, filtered_df)
                col1, col2 = st.columns(2)

                with col1:
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df[1], labels=emoji_df[0], colors=sns.color_palette("Set3", len(emoji_df[0])))
                    st.pyplot(fig)

                with col2:
                    st.dataframe(emoji_df)
