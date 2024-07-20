import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics


#The Model
data = pd.read_csv("2.0/PremDataProcessed.csv")
data = data.drop(columns=["Position", "Average_Market_Value", "Unnamed: 0"])

latest_year_df = data.tail(20)
latest_year_df = latest_year_df[latest_year_df["Year"] == max(latest_year_df["Year"].tolist())]

data = data.head(len(data) - 20)

# Selecting the features and target variable
features = ['Goal_Difference', 'Normalized_Average_Market_Value']
X = data[features]
y = data['Points']

# Splitting the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Creating the model
multi_lin_reg_model = LinearRegression()

# Fitting the model
multi_lin_reg_model.fit(X_train, y_train)

# Making predictions
predictions = multi_lin_reg_model.predict(X_test)

# Calculating the MAE
mae = metrics.mean_absolute_error(y_test, predictions)

inputs = ["Goal_Difference", "Normalized_Average_Market_Value"]
predictions = multi_lin_reg_model.predict(latest_year_df[inputs])
latest_year_df["Predicted_Points"] = predictions.round()

latest_year_df.sort_values(by="Predicted_Points", ascending=False, inplace=True)
latest_year_df = latest_year_df[["Year", "Team", "Normalized_Average_Market_Value", "Goal_Difference", "Goal_Difference", "Points", "Predicted_Points"]]


st.write("""
# Premier League Prediction Model
""")

teams = latest_year_df["Team"].tolist()
team = st.radio("Pick a team to predict", teams)

index = latest_year_df["Team"].tolist().index(team)
st.write("# Number of points: ", latest_year_df["Predicted_Points"].tolist()[index])