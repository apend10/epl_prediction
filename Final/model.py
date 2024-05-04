#imports
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn import metrics

#STEP 1:
#webscrape data, remove unnecessary columns, create NAMV
def prepare_data(filepath):
    #gather data
    data = pd.read_csv(filepath)

    relativeValue = []

    #create a normalized_average_market_value column
    #Loop through each row
    for index, team in data.iterrows():
        
        #Obtain which season we are looking at
        season = team['Year']
        
        #Create a new dataframe with just this season
        teamseason = data[data['Year'] == season]
        
        #Find the max value
        maxvalue = teamseason['Average_Market_Value'].max()
        
        #Divide this row's value by the max value for the season
        tempRelativeValue = team['Average_Market_Value']/maxvalue
        
        #Append it to our list
        relativeValue.append(tempRelativeValue)

    #Add list to new column in main dataframe
    data["Normalized_Average_Market_Value"] = relativeValue

    data = data.drop(columns=["Total_Market_Value", "Squad_Size", "Number_of_Foreigners", "Average_Age", "Unnamed: 0"])
    return data

#STEP 2:
def create_gd_predictions(input_data):
    gd_data = input_data.drop(columns=["Position", "Points", "Average_Market_Value"])
    gd_data_wo_2022 = gd_data.head(len(gd_data) - 20)
    teams2223 = gd_data[gd_data["Year"] == 2022]["Team"].unique().tolist()

    def gd_namv_prediction_model(num_degrees = 2, std_dev = 18, plots = False):
        gd_namv_predictions = []
        
        for i in range(20):
            team = teams2223[i]
            team_df = gd_data_wo_2022[gd_data_wo_2022['Team'] == team]

            degrees = 1
            if not team_df.empty: 
                team_std_dev = team_df['Goal_Difference'].std()

                if(team_std_dev > std_dev):
                        degrees = num_degrees

                x = team_df['Normalized_Average_Market_Value']
                y = team_df['Goal_Difference']

                x = x.values.reshape(-1,1)
                y = y.values.reshape(-1,1)

                poly = PolynomialFeatures(degree= degrees, include_bias=False)
                poly_features = poly.fit_transform(x)
                poly_reg_model = LinearRegression()
                poly_reg_model.fit(poly_features, y)

                y_predicted = poly_reg_model.predict(poly_features)

                predictions = poly_reg_model.predict(poly_features)

                namv = [[gd_data_wo_2022["Normalized_Average_Market_Value"][i]]]
                poly23 = poly_features = poly.fit_transform(namv)
                gd_namv_predictions.append(poly_reg_model.predict(poly23))
                gd_namv_predictions[i] = gd_namv_predictions[i][0][0].round()
                
                if(plots):
                    print(team)
                    print("Standard Deviation:", team_std_dev)
                    print("y(" + str(gd_data_wo_2022["Normalized_Average_Market_Value"][i]) + ") =", gd_namv_predictions[i])
                    print("_____________________________")

                    plt.scatter(x, y, color = 'purple')
                    plt.plot(x, y_predicted, color = 'green', linewidth = 3)
                    plt.xlabel("Normalized Average Market Value (namv)")
                    plt.ylabel("Goal Difference")
                    plt.show()

            else: 
                gd_namv_predictions.append(-30)
                if(plots):
                    print(team)
                    print("No data for this team!")
                    print("_____________________________")
        return gd_namv_predictions
    def gd_year_prediction_model(num_degrees = 3, std_dev = 12, plots = False):
        gd_year_predictions = []

        for i in range(20):
            team = teams2223[i]
            team_df = gd_data_wo_2022[gd_data_wo_2022['Team'] == team]

            degrees = 1
            if not team_df.empty: 
                team_std_dev = team_df['Goal_Difference'].std()

                if(team_std_dev > std_dev):
                    degrees = num_degrees

                x = team_df['Year']
                y = team_df['Goal_Difference']

                x = x.values.reshape(-1,1)
                y = y.values.reshape(-1,1)

                poly = PolynomialFeatures(degree= degrees, include_bias=False)
                poly_features = poly.fit_transform(x)
                poly_reg_model = LinearRegression()
                poly_reg_model.fit(poly_features, y)

                y_predicted = poly_reg_model.predict(poly_features)

                poly22 = poly_features = poly.fit_transform([[2022]])
                gd_year_predictions.append(poly_reg_model.predict(poly22))
                gd_year_predictions[i] = gd_year_predictions[i][0][0].round()

                if(plots):
                    plt.scatter(x, y, color = 'purple')
                    plt.plot(x, y_predicted, color = 'green', linewidth = 3)
                    plt.title(f"{team} - gd prediction \nStd Dev: {team_std_dev:.2f}, GD for 2022/23: {gd_year_predictions[i]}")
                    plt.xlabel("Year")
                    plt.ylabel("Goal Difference")
                    plt.xticks(x.flatten(), rotation=90)  # Adjusting x-axis to show all labels
                    plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
                    plt.show()

            else:
                #No data for a team
                gd_year_predictions.append(-30)

        return gd_year_predictions

    gd_namv_predictions = gd_namv_prediction_model()
    gd_year_predictions = gd_year_prediction_model()

    final_predictions = []
    for i in range(20):
        prediction = round(gd_year_predictions[i] * 0.40  + gd_namv_predictions[i] * 0.60)
        final_predictions.append(prediction)

    return final_predictions

#STEP 3:
def create_model(data):
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

    # Displaying the metrics
    print(f"Mean Absolute Error: {mae}")

    return multi_lin_reg_model

#STEP 4:
def predict(gd_predictions, model):
    data2023 = pd.read_csv("2023PremData.csv")
    data2023 = data2023[["Team", "Average_Market_Value"]]
    for i in range(20):
        data2023["Average_Market_Value"][i] /= 57.74
    data2023.rename(columns={"Average_Market_Value": "Normalized_Average_Market_Value"}, inplace=True)
    data2023["Goal_Difference"] = gd_predictions
    data2023["Predicted Points"] = model.predict(data2023[["Goal_Difference", "Normalized_Average_Market_Value"]])

    return data2023

def main():
    data = prepare_data("PremData.csv")

    gd_predictions = create_gd_predictions(data)
    model = create_model(data)
    print(predict(gd_predictions, model))


if __name__ == "__main__":
    main()