CBT is a command-line tool used to interact with Cloud Bigtable from Cloud Shell or your local machine.

gcloud config set project YOUR_PROJECT_ID

echo project = YOUR_PROJECT_ID > ~/.cbtrc echo instance = YOUR_INSTANCE_ID >> ~/.cbtrc

cbt createtable employee

cbt createfamily employee profile

cbt set employee emp#1001 profile:name=Varinder cbt set employee emp#1001 profile:city=Delhi cbt set employee emp#1001 profile:salary=50000

cbt set employee emp#1002 profile:name=Amit cbt set employee emp#1002 profile:city=Mumbai cbt set employee emp#1002 profile:salary=60000

Employee 1003

cbt set employee emp#1003 profile:name=Neha cbt set employee emp#1003 profile:city=Pune cbt set employee emp#1003 profile:salary=70000 cbt set employee emp#1003 profile:department=HR cbt set employee emp#1003 profile:active=true

Employee 1004

cbt set employee emp#1004 profile:name=Rahul cbt set employee emp#1004 profile:city=Bangalore cbt set employee emp#1004 profile:salary=90000 cbt set employee emp#1004 profile:department=IT cbt set employee emp#1004 profile:active=false

Employee 1005

cbt set employee emp#1005 profile:name=Priya cbt set employee emp#1005 profile:city=Chandigarh cbt set employee emp#1005 profile:salary=80000 cbt set employee emp#1005 profile:department=Marketing cbt set employee emp#1005 profile:active=truez

cbt read employee

cbt read employee prefix=emp#1001