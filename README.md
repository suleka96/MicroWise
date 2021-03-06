![picture](images/logo.png)

<h1>MicroWise</h1>

MicroWise is a console based application that, when given the desired optimization and tuning parameter configurations, optimizes the performance of a given JVM-based Microservice. A dashboard is also available to analyse the overview of the optimization process. MicroWise optimizes the underlying JVM parameters that effect GC to obtain a performance gain in the Microservice. 

#### Prerequisites
* Python 3

<h2>How to Use?</h2>
step 01: Clone the project 


step 02: Install dependencies
````````````````````````````````````
cd MicroWise
pip3 install -r requirements.txt
````````````````````````````````````

step 03: Navigate into the project's optimizer folder
````````````````````````````````````
cd optimizer
````````````````````````````````````

step 04: Copy Microservice jar inside this folder

step 05: Execute MicroWise
````````````````````````````````````
python3 Optimizehyperopt.py
````````````````````````````````````

<h2>How to View Results?</h2>
The <b>all_results</b> folder inside the optimization folder containes all the result files created during the optimization process. The <b>final optimal JVM parameter configuration that effect GC</b> can be found in the <b>final_parameter_configuration.txt</b> file. 

<h2>How to Access Dashboard?</h2>
At the end of the optimization the url for the dashboard will be given. Simply copy and paste the url into your browser.

## Built With

* [Dash](https://plotly.com/dash/) 
* [Hyperopt](http://hyperopt.github.io/) 
* [Scikit-Learn](https://scikit-learn.org/stable/)
