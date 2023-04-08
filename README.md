<p align="center">
        <iframe width="2279" height="949" src="https://www.youtube.com/embed/VpFshPQstlU" title="Automated Sales Analysis Dashboard Generator" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</p>
<h1 align="center"> Data Analyzer </h1>

This repository contain a project which can automatically generate a dashboard for sales analysis from the provided data. You just need to specify some details required at the start for processing data. Then the code will automatically preprocess and create interactive plotly plots. Also it will then generate a Dashboard using Dash Framework.


## How to test provided sample data ?
* The data and CSS for Dashboard is provided in assets folder. Then to run there are two ways to test sample data:

    1. Jupyter Notebook
        * You can open jupyter notebook (Main.ipynb) file  and can change the details if required also you can check how plots are generated on each step. At the end a pickle file will be generated as a dictionary containing all dataframe and plot.
        * After this you can run the Dashboard.py file in terminal, this will generate a Dashboard using data of our pickle file.
    2. Python 
        * Directly run the P_Main file in terminal you will get a Dashboard Server link where you can check the dashboard.


# 🎇How to Work on New Data🎇

* Provide your new data file in assets folder then you can work in two ways:

    1. Jupyter Notebook
        * You can open jupyter notebook (Main.ipynb) file and can change the details as mentioned in ipynb file step by step.
        * After this you can run the Dashboard.py file in terminal, this will generate a Dashboard using data of our pickle file.