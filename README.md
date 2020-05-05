# COVID-19 Dashboard for Canada

I build this dashboard to better understand the situation of COVID-19 outbreak in Canada. It is made by pure python thanks for [dash](https://plotly.com/dash/). I also deployed it to Heroku (https://wayneyin-covid19-dashboard.herokuapp.com/). 

All data come from the official website of the [Public Health Department of Canada](https://www.canada.ca/en/public-health/services/diseases/coronavirus-disease-covid-19.html). Though the government has its official [dashboard](https://experience.arcgis.com/experience/2f1a13ca0b29422f9b34660f0b705043/), my dashboard provide more detail about test number and the news about COVID-19 in Canada. 

Feel free to contact me if you have any question.

## Table of Contents

- [Contact](#contact)
- [Install](#install)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Contact

+ email: wayneyinwork@outlook.com
+ Twitter: [MiaoMiaoMiao](https://twitter.com/wayneyin777)

## Install

The dependencies needed are in requirements.txt. It will be better to create a [virtual environment](https://docs.python.org/3/library/venv.html) for this project to avoid mess up your own environment.

```sh
$ pip install -r requirements.txt
```

## Usage

You can directly visit https://wayneyin-covid19-dashboard.herokuapp.com/ in your web browser or

Run `covid19dashboard/app.py` on your local machine and visit http://127.0.0.1:8050/ in your web browser.

+ This project use SQLite as the database and it is located in `data/COVID19.db`

+ The logo image and CSS file for the dashboard are in `covid19dashboard/assets`
+ This project use [dotenv](https://pypi.org/project/python-dotenv/) to store API key for [News API](https://newsapi.org/). If you want to see the news update part in the dashboard please register your own News API KEY on https://newsapi.org/ and store it by create a new file named `.env`. See detail on dotenv official document: https://pypi.org/project/python-dotenv/

## Contributing



## License

[MIT © Wayne Yin.](../LICENSE)