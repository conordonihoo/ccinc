# COE 332 Final Project: CC Banking Inc
#### Conor Donihoo and Cameron Cummins

## Description

The goal of [this](https://isp-proxy.tacc.utexas.edu/conor/) web application was to create a system in python using the Flask API for keeping track of simple bank accounts with deposit and withdraw functions. On top of this system, we also developed a browser-friendly user interface using HTML, CSS, and JavaScript. The database is sustained using Redis and the network is orchestrated with kubernetes.

The docker image for this application can be found [here](https://hub.docker.com/r/conordonihoo/coe332final).

All of the data is randomly generated using a preconfigured set of normal distributions. Since the data is generated, the dataset can be expanded to any size the user desires.

We developed functions for creating both large datasets and individual accounts.

On top of basic CRUD functionality, we implemented some simple analysis features:
- A graph and polynomial regression of the spending habits of an individual account over time
- A histogram of the number of transactions per hour of an individual account

## Loading Page
![](https://i.imgur.com/W9a4I9C.png)

The landing page consists of four sections: the login pane, the ID pane, the description pane, and the active jobs table.

### Login Pane
![login pane](https://i.imgur.com/8M0s6S2.png)

To login to a specific account, enter the account ID and click the "Login" button. If you want to create a new account with a new ID, click "Create New Account" and it will automatically generate an ID and access the account.
For creating datasets, you can use the "Generate 100 Random Accounts" to create 100 unique accounts with hundreds of transactions over two decades using a two preset normal distributions. These distributions describe the transaction amounts (negative indicating a withdrawal).
- 50 accounts generated with μ = 15 and σ = 20
- 50 accounts generated with μ = 75 and σ = 15

To clear the entire database, click "Nuke All Accounts".

### ID Pane
![id pane](https://i.imgur.com/JHKEbil.png)

The ID pane is updated every 10 seconds with a list of all the account IDs stored in the database.

### Active Jobs Table
![](https://i.imgur.com/1u9HSO9.png)

This table displays all of the active jobs in the system. It updates every 10 seconds and only displays each job once to prevent too much overloading.

## Account Page
![](https://i.imgur.com/1V4Yk6I.png)

The landing page consists of four sections: the account controls, transaction table, and analysis graphs.

### Account Controls
![](https://i.imgur.com/KVs0cP9.png)

The controls indicate what account you are currently logged into and provide functions for making withdrawals and deposits. You cannot withdraw more than the balance. Clicking the "Logout" logs you out of the account and returns you to the landing page. Clicking "Close Acocunt" deletes this account from the database.

### Transaction Table
![](https://i.imgur.com/hNnMzJo.png)

The table shows all transactions that have taken place on this account.

### Analysis Graphs
![](https://i.imgur.com/FRi5hFF.png)

The spending graph displays the balance of the account over time. The blue line indicates the actual balance while the dashed red line indicates the predicted balance from the polynomial regressor.

![](https://i.imgur.com/zhOuXGB.png)

The histogram displays the number of transactions that took place each hour.



## Routes
#### `/transaction/deposit`
> Adds an amount of money in a specified account using parameters `amount` and `id` respectively

#### `/transaction/withdraw`
> Removes an amount of money in a specified account using parameters `amount` and `id` respectively

#### `/nuke` 
> Deletes all accounts and jobs in all of the databases

#### `/generate_accounts`
> Generates 100 unique, randomly populated accounts

#### `/graph/histogram`
> Generates and returns a .png file of a histogram of the number of transactions per hour associated with an account specified by `id`

#### `/graph/spending`
> Generates and returns a .png file of a line graph of the balance of an account specified by `id` over time

#### `/jobs`
> Returns a JSON-serializeable list of active jobs and their descriptive dictionaries

#### `/jobids`
> Returns a JSON-serializeable list all active job IDs

#### `/accountids`
> Returns a JSON-serializeable list all account IDs

#### `/delete`
> Deletes the account specified by `id`

#### `/create`
> Creates a new account and returns its ID

#### `/login`
> Returns a JSON-serializeable dictionary of the account specified by `id`

#### `/` 
> Returns the HTML template for the user-interface

## Redis Databases

#### `rd1`
> stores transaction jobs that communicate with `worker_transaction.py`

#### `rd2`
> stores all the accounts and their information

#### `rd3`
> stores graphing jobs that communicate with `worker_graph.py`

#### `rd4`
> stores all jobs for the purpose of displaying them on the html page

#### `q1`
> queue for transactions

#### `q2`
> queue for graphs

## Workers

List workers and describe what each worker does

#### `worker_transaction.py`
> processes transaction (withdrawal/deposit) jobs by taking them out of `q1`

#### `worker_graph.py`
> processes graph jobs by taking them out of `q2`

## C.R.U.D. Criteria Met

List and explain how we satisfied each CRUD criteria

### Create
###### These routes create data:
* `/generate_accounts`
* `/create`

### Read
###### These routes read data:
* `/jobs`
* `/jobids`
* `/accountids`
* `/graph/histogram`
* `/graph/spending`
* `/login`
* `/`

### Update
###### These routes update data:
* `/transaction/withdraw`
* `/transaction/deposit`

### Delete
###### These routes delete data:
* `/delete`
* `/nuke`




















































