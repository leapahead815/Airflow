 
import json
import pathlib
import airflow
import requests
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
 
​
dag = DAG(
dag_id="download_rocket_launches",
start_date=airflow.utils.dates.days_ago(14),
schedule_interval=None,
)
​
#task 1 fetching josn data through bash command. 一条bash命令就可以从指定URL获取网页数据并存入tmp文件夹下的launches.json文件中
download_launches = BashOperator( 
task_id="download_launches",
bash_command="curl -o /tmp/launches.json
'https://launchlibrary.net/1.4/launch?next=5&mode=verbose'",
dag=dag,  #all tasks within the same DAG reference this dag 
​
​
​
#从launches.json中读出URL地址，下载对应的images，存入/tmp/images 文件夹
def _get_pictures():   
​
    pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True) # Ensure directory exists
 
    with open("/tmp/launches.json") as f:
        launches = json.load(f)
        image_urls = [launch["rocket"]["imageURL"] for launch in launches["launches"]]
    
        for image_url in image_urls:
            response = requests.get(image_url)  
            image_filename = image_url.split("/")[-1]
            target_file = f"/tmp/images/{image_filename}"
    
            with open(target_file, "wb") as f:  #将对应URL的图片存入电脑的target_file中
                f.write(response.content)
            print(f"Downloaded {image_url} to {target_file}")
    
    
#task 2    
#run a Python function    
get_pictures = PythonOperator(
task_id="get_pictures",
python_callable=_get_pictures,  #调用哪个python function
dag=dag,
)
​
#task 3
#显示下载了多少张图片
notify = BashOperator(
task_id="notify",
bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
dag=dag,
)
​
#To make sure the tasks run in the correct order
download_launches >> get_pictures >> notify