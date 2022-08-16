[![Geo Scatter](https://raw.githubusercontent.com/wrny/plotly_ivt_geo_dashboard/master/geo_scatter.png?raw=true "Geo Scatter")](https://raw.githubusercontent.com/wrny/plotly_ivt_geo_dashboard/master/geo_scatter.png?raw=true "Geo Scatter")

# A Geo Scatter Dashboard of Invalid Web Traffic built with Plotly and Dash

On behalf of a client, I built a dashboard in Plotly and Dash for a client that shows website bot traffic by geographic location. Bot vs. not analysis along with geographic location was done using a bot detection tool we built entirely in-house. The size of the circle glyphs on the map correspond to the total number of hits recorded in that city or town.

This dashboard features: 

* A clickable legend to isolate locations with higher + lower percentages of bot traffic
* A "Population Slider" that lets viewers alter the plots on the map with higher and lower popualations. If you only want to see areas with 1000 or more hits, you can do that here.
* A "Download CSV" button that lets users look at the actual raw data in Excel.
* An interactive "Data Table" with raw stats that also changes depending on the slider's value.
* Zoom, Pan and Box select, and other Plotly / Dash features

The dashboard can be viewed online here:
[http://18.218.126.178/](http://18.218.126.178/ "http://18.218.126.178/")

## To Install:

**In AWS**: 
* Create a standard EC2 instance Ubuntu 20.04. I chose a t2.micro instance.
* Go to security security groups for the instance and open port 80 to inbound traffic.

**In the instance (access via SSH, Remina, PuTTY, etc.)**

`sudo apt update` \
`sudo apt upgrade` \
`sudo git clone https://github.com/wrny/plotly_ivt_geo_dashboard` \
`cd plotly_ivt_geo_dashboard` \
`sudo apt-get install python3.8-venv` \
`sudo apt-get install python3-pip` \
`sudo python3 -m venv venv` \
`source venv/bin/activate` \
`sudo pip3 install -r requirements.txt` \
`sudo pip3 install gunicorn` \
`pkill gunicorn`

`sudo apt install nginx` \
`sudo nano /etc/nginx/sites-enabled/plotly_ivt_geo_dashboard`

* You'll get a blank file. Paste what's below with the proper IP address where it reads YOUR_IP_ADDRESS_HERE. Formatting now: unless you have four space where the tabs are (and eight spaces where two tabs are) NGINX won't start properly.

>server { \
>&emsp;listen 80; \
>&emsp;server_name YOUR_IP_ADDRESS_HERE; \
>&emsp;location / { \
>&emsp;&emsp;proxy_pass http://127.0.0.1:8000; \
>&emsp;&emsp;proxy_set_header Host $host; \
>&emsp;&emsp;proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
>&emsp;} \
>}


`sudo unlink /etc/nginx/sites-enabled/default` \
`sudo nginx -s reload`

**Activate the Dashboard**

`tmux` \
`gunicorn -b 0.0.0.0:8000 main:server`

And it's done.

To test, paste the IP address where the dashboard is hosted.
