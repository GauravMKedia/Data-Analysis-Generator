### Dashboard Preview:
<p align="center">
  <img src="https://i.imgur.com/kNMoNQI.gif" alt="animated" style="border: 5px solid black">
</p>
<h1 align="center"> Data Analyzer </h1>

This repository contain a project which can automatically generate a dashboard for sales analysis from the provided data. You just need to specify some details required at the start for processing data. Then the code will automatically preprocess and create interactive plotly plots then it will generate a Dashboard using Dash Framework.
I have created a dashboard on Sample Sales Data from Kaggle provided in assets folder.
Dashboard => 

## How to test provided sample data ?
* The data and CSS for Dashboard is provided in assets folder. Then to run there are two ways to test sample data:

    1. Jupyter Notebook
        * You can open jupyter notebook (Main.ipynb) file  and can change the details if required also you can check how plots are generated on each step. At the end a pickle file will be generated as a dictionary containing all dataframe and plot.
        * After this you can run the Dasboard using Dashboard.py file in terminal, this will generate a Dashboard using data of our pickle file.
    2. Python 
        * Directly run the Main.py file in terminal you will get a Dashboard Server link where you can check the dashboard.


## How to Work on New Data ?

* Provide your new data file in assets folder then you can work as:
    1. Jupyter Notebook
        * You can open jupyter notebook (Main.ipynb) file and can change the details as mentioned in ipynb file step by step.
        * After this you can run the Dashboard.py file in terminal, this will generate a Dashboard using data of our pickle file.
