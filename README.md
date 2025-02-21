# transactionsimulation
|Tool                | Description                    | Tags for tools used                                                                                               |
| ------------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------- |
| 1.GitHub| Version Control| [Version-Control]; [Repo];|
| 2.Django |  Python Based Backend Framework| [python]; [Django];|
| 3.PostgresQl | Relational Database| [Relational Integrity]; [Database];|
| 4.Virtual env | Package manager| [Virtual Environment];[Dependency];|
| 5.Redis | in-memory Cache Manager| [Cache Manager];|

## <h1> Description</h1>
<p>The aim of the project is to build a transaction simulation api that authenticates users, enables user to transact,view balances and retrieve transaction history </p>

## <h1> Features</h1>
<ul>
<li>Admin dashboard to view lists of users and transactions,blacklist tokens</li>
<li>Redis for cache management of transactions</li>
<li>Throttler to limit sign up and login attempts and pagination</li>
</ul>

## <h1> Set up Instructions</h1>
<p><b>Github</b></p>
<ul>
<li> Download the Zip file from the code tab on github to get the project Zip files (Recommended)</li>
<li> Clone the project using 'git clone https://github.com/andrewindeche/transactionsimulation.git'.</li>
<li> Unzip the file and add the Project folder to your IDE/Compiler</li>
</ul>

<p><b>Docker</b></p>
Python 3.13.2 Django==5.1.6

1. Create an .env environment on the Django root folder and add the recessary environment variables. 
Use <b>env.example</b> as a guide for environment variables.

CREATE DATABASE database;

CREATE USER newuser WITH PASSWORD 'newpassword';

GRANT ALL PRIVILEGES ON DATABASE database TO myuser;


9. Access the Django development server on:

<b>http://localhost:8000/</b> 


<p><b>Django</b></p>

<p>The project uses virtual env, django and postgresql backend</p>

1. Install virtual using the command 

```bash
python3.13 -m venv virtual
```

2. Activate your virtual enviromnment

```bash
source virtual/bin/activate
```

3. Navigate to your Django project and use  in  the directory path: <b>backend\requirements.txt</b> to install the required django dependencies 

```bash
pip3 install -r requirements.txt
```

4. Create an .env on the Django root folder and add the recessary environment variables. 

Use (env.example) as a guide for environment variables </li>

5. Create a Super User using 

```bash
python3 manage.py createsuperuser
```

6. Migrate your DB using 

```bash
python3 manage.py migrate
```

7. To run the project use: 

```bash
 python3 manage.py runserver
```

8. Open the server using the link : 

<b>http://localhost:8000</b>

9. Open the Redis server using :

```bash
redis-cli
```

Check for cached keys

```bash
KEYS transaction_history_*
```
Inspect cached data

```bash
GET transaction_history_123
```
## <h1> Indexes Applied to optimize database</h1>
-- speed up queries that filter or join the Transaction model based on the user field
CREATE INDEX idx_transaction_user ON transactions_transaction(user_id);

--  improve the speed of queries filtering by transaction_type
Retrieving all deposits or withdrawals from the Transaction table.
Running reports or analyses that group or count transactions by type
CREATE INDEX idx_transaction_type ON transactions_transaction(transaction_type);

--  This index is crucial for speeding up queries that filter by the user's email address
CREATE INDEX idx_user_email ON transactions_user(email);

## <h1> Throttle Rate Limits</h1>
API calls have been limited for logins and sigups at a daily rate
        'anon': '40/day', 
        'user': '40/day',
        'login': '50/minute',
        'signup': '60/minute'


## <h1> Endpoints</h1>

1. Signing up:
<p><b>POST:http://localhost:8000/api/register/</b></p>
    example raw payload:
    {
        "username": "paul",
        "email":"paul@abc.com",
        "first_name":"Paul",
        "last_name":"Walker",
        "password":"Complexpasword#"
     }

2. Logging in:
<p><b>POST:http://localhost:8000/api/login/</b></p>
    example raw payload:
    {
        "username_or_email": "username",
        "password":"Password35$"
    }

3. Refresh Token:
<p><b>POST:http://localhost:8000/api/token/refresh/</b></p>
    example raw payload:
    {
        "token":"TOKEN-ABC"
    }

4. Get Account Details:
<p><b>GET: http://localhost:8000/api/account/</b></p>
    Headers: Authorization: Bearer <your_jwt_access_token>

5.Create a Transaction (Deposit/Withdrawal):
<p><b>POST: http://localhost:8000/api/transaction/</b></p>
    example raw payload:
    Deposit
    {
    "transaction_type": "deposit",
    "amount": 100.50
    }

    Withdrawal
    {
    "transaction_type": "withdrawal",
    "amount": 50.00
    }

6.Get Transaction History:
<p><b>GET: http://localhost:8000/api/transactions/</b></p>
Authorization: Bearer <your_jwt_access_token>


## <h1> Author </h1>
Built by <b>Andrew Indeche</b>