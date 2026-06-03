# 说明文档
## 项目概述
本项目为一款新能源汽车价格预测分析系统，主要是基于XGBoost模型为预测核心模型算法，目前仅采用汽车之家往年数据进行训练，且为固定模型参数，未来将结合MLP综合大模型进行估价与动态爬虫模块。
## 项目技术栈
本项目前端采用Vue.js框架，结合路由管理以及状态管理，采用Echarts制作可视化图表；后端采用Django框架，Django Restful API接口规范，数据库为PostgreSQL（支持mysql与sqllite3），便于与Django进行后台管理。
## 特别申明
本项目目前已开源，其中大部分代码由AI辅助生成，主要分享全栈开发框架经验（本人是大学生），最后希望社区支持，我将完成这些未来开发模块
# Documentation
## Project Overview
This project is a new energy vehicle price prediction and analysis system, mainly based on the XGBoost model as the core prediction algorithm. Currently, it only uses historical data from Autohome for training, with fixed model parameters. In the future, it will integrate an MLP-based comprehensive large model for pricing and a dynamic web scraping module.

## Project Technology Stack
The front end of this project uses the Vue.js framework, combined with routing management and state management, and utilizes ECharts to create visual charts;
The back end uses the Django framework and follows Django Restful API specifications,
The database is PostgreSQL(Supports MySQL and SQLite3), which facilitates backend management with Django.

## Special Statement
This project is currently open source. Most of the code was generated with AI assistance, mainly sharing full-stack development framework experience (I am a university student). Finally, I hope for community support, and I will complete these future development modules.
# 项目说明
## 项目结构说明
```
NEV_Price_System/                        # 项目根目录
│
├── manage.py                            # Django 管理入口
├── requirements.txt                     # Python 依赖清单
├── .env.example                         # 后端环境变量模板
│
├── NEV_Price_System/                    # Django 项目配置包
│   ├── settings.py                      # 全局配置
│   ├── urls.py                          # 根路由汇总
│   ├── wsgi.py                          # WSGI 部署入口
│   └── asgi.py                          # ASGI 部署入口
│
├── users/                               # 用户模块
│   ├── models.py                        # User 模型
│   ├── serializers.py                   # 注册/用户序列化器
│   ├── views.py                         # 注册、登录、个人信息 API
│   ├── views_admin.py                   # 管理员用户管理 ViewSet
│   ├── urls.py                          # 用户模块路由
│   └── migrations/                      # 数据库迁移文件
│
├── cars/                                # 车型与预测模块
│   ├── models.py                        # Car、MLModel、PredictionHistory、FavoriteCar
│   ├── serializers.py                   # 车型序列化器
│   ├── views.py                         # 车型 CRUD API
│   ├── views_dashboard.py               # 首页仪表盘统计 API
│   ├── views_predict.py                 # 价格预测、模型管理、相似车型 API
│   ├── views_favorites.py               # 收藏相关 API
│   ├── admin.py                         # Django Admin 注册
│   ├── urls.py                          # 车型模块路由汇总
│   ├── migrations/                      # 数据库迁移文件
│   └── management/
│       └── commands/
│           ├── import_data.py           # 从 Excel 导入车型数据
│           ├── update_data.py           # 从 Excel 更新车型数据
│           └── train_model.py           # 训练 XGBoost 模型并入库
│
├── scripts/                             # 离线分析脚本
│   ├── train_model_visual.py            # 终端训练过程可视化 + R²/RMSE
│   ├── shap_analysis.py                 # SHAP 特征重要性 + 学习曲线 + 残差分析
│   ├── data_statistics.py               # 原始/筛选数据统计图 + 重要性比对
│   ├── evaluate_model.py                # 模型评估报告输出
│   ├── extract_features.py              # 特征提取脚本
│   └── feature_analysis.py              # 特征分析脚本
│
├── static/                              # 静态资源
│   ├── data/
│       └── car_data_15features.xlsx     # 车辆原始数据集
│
└── frontend/                            # Vue 3 前端项目
    ├── package.json                     # 前端依赖清单
    ├── vite.config.js                   # Vite 构建配置
    ├── tsconfig.json                    # TypeScript 配置
    ├── index.html                       # 入口 HTML
    ├── .env                             # 前端环境变量
    ├── .env.example                     # 前端环境变量模板
    │
    └── src/
        ├── main.js                      # Vue 应用入口
        ├── App.vue                      # 根组件
        ├── env.d.ts                     # 环境变量类型声明
        │
        ├── assets/
        │   └── styles/
        │       └── variables.scss       # 全局 CSS 变量与主题
        │
        ├── router/
        │   └── index.js                 # Vue Router 路由配置
        │
        ├── stores/
        │   └── user.js                  # Pinia 用户状态管理
        │
        ├── utils/
        │   └── axios.js                 # Axios 实例与拦截器
        │
        └── views/
            ├── System.vue               # 主布局框架（侧边栏 + 顶栏）
            │
            ├── auth/                    # 认证页面
            │   ├── Login.vue            # 登录页
            │   └── Register.vue         # 注册页
            │
            ├── core/                    # 核心功能页面
            │   ├── FirstView.vue        # 仪表盘首页
            │   ├── MarketView.vue       # 市场车型浏览与收藏
            │   ├── PredictView.vue      # 价格预测
            │   ├── AnalysisView.vue     # 市场分析
            │   ├── FavoritesView.vue    # 我的收藏
            │   ├── HistoryView.vue      # 预测历史记录
            │   └── HelpView.vue         # 帮助中心
            │
            ├── user/                    # 用户中心
            │   ├── ProfileView.vue      # 个人资料
            │   └── SettingsView.vue     # 系统设置
            │
            ├── admin/                   # 后台管理
            │   ├── AdminView.vue        # 车型数据管理
            │   ├── UserManageView.vue   # 用户管理
            │   └── ModelAdminView.vue   # 模型版本管理
            │
            └── error/
                └── NotFound.vue         # 404 页面
```
# Project Description
## Project Structure Description
```
NEV_Price_System/                        # Project root directory
│
├─ manage.py                            # Django management entry point
├─ requirements.txt                     # Python dependency list
├─ .env.example                          # Backend environment variable template
│
├─ NEV_Price_System/                    # Django project configuration package
│   ├─ settings.py                      # Global configuration
│   ├── urls.py                          # Root route aggregation
│   ├── wsgi.py                          # WSGI deployment entry point
│   └── asgi.py                          # ASGI deployment entry point
│
├─ users/                               # User module
│   ├─ models.py                          # User model
│   ├─ serializers.py                   # Registration/User Serializer
│   ├─ views.py                          # Registration, login, personal information API
│   ├─ views_admin.py                   # ViewSet for managing admin users
│   ├── urls.py                          # User module routing
│   └── migrations/                      # Database migration files
│
├─ cars/                                # Vehicle models and prediction module
│   ├─ models.py                          # Car, MLModel, PredictionHistory, FavoriteCar
│   ├─ serializers.py                   # vehicle model serializer
│   ├─ views.py                          # Vehicle model CRUD API
│   ├─ views_dashboard.py               # Home dashboard statistics API
│   ├─ views_predict.py                 # Price prediction, model management, similar vehicle model API
│   ├── views_favorites.py               # Favorites-related API
│   ├─ admin.py                          # Django Admin registration
│   ├── urls.py                          # Model module routing summary
│   ├─ migrations/                      # Database migration files
│   └── management/
│       └── commands/
│           ├─ import_data.py           # Import vehicle model data from Excel
│           ├─ update_data.py           # Update vehicle model data from Excel
│           └── train_model.py           # Train the XGBoost model and load it into the library
│
├─ scripts/                             # Offline analysis scripts
│   ├─ train_model_visual.py            # Terminal training process visualization + R²/RMSE
│   ├── shap_analysis.py                 # SHAP feature importance + learning curve + residual analysis
│   ├─ data_statistics.py               # Original/filtered data statistics chart + importance comparison
│   ├─ evaluate_model.py                # Output of model evaluation report
│   ├─ extract_features.py              # Feature extraction script
│   └── feature_analysis.py              # Feature analysis script
│
├─ static/                              # Static resources
│   ├── data/
│       └── car_data_15features.xlsx     # Original vehicle dataset
│
└── frontend/                            # Vue 3 frontend project
    ├─ package.json                     # Front-end dependency list
    ├─ vite.config.js                   # Vite build configuration
    ├─ tsconfig.json                    # TypeScript configuration
    ├─ index.html                       # Entry HTML
    ├─ .env                             # Front-end environment variables
    ├─ .env.example                     # Front-end environment variable template
    │
    └── src/
        ├─ main.js                      # Vue application entry
        │   ├─ App.vue                      # Root component
        ├─ env.d.ts # Environment variable type declaration
        │
        ├── assets/
        │   └── styles/
        │       └── variables.scss       # Global CSS variables and themes
        │
        ├── router/
        │   └── index.js                 # Vue Router routing configuration
        │
        ├── stores/
        │   └── user.js                  # Pinia user state management
        │
        ├── utils/
        │   └── axios.js                 # Axios instance and interceptor
        │
        └── views/
            │   ├─ System.vue               # Main layout framework (sidebar + header)
            │
            ├─ auth/                    # Authentication page
            │   ├─ Login.vue            # Login page
            │   └── Register.vue         # Registration page
            │
            ├─ core/                    # Core functional pages
            │   ├─ FirstView.vue        # dashboard homepage
            │   ├─ MarketView.vue       # Market vehicle browsing and collection
            │   ├─ PredictView.vue      # Price Prediction
            │   ├─ AnalysisView.vue     # Market Analysis
            │   ├─ FavoritesView.vue    # My Favorites
            │   ├─ HistoryView.vue      # Prediction history
            │   └── HelpView.vue         # Help Center
            │
            ├─ user/                    # User center
            │   ├─ ProfileView.vue      # 个人资料
            │   └── SettingsView.vue     # System Settings
            │
            ├─ admin/                   # Back-end management
            │   ├─ AdminView.vue        # Vehicle model data management
            │   ├─ UserManageView.vue   # User Management
            │   └── ModelAdminView.vue   # Model Version Management
            │
            └── error/
                └── NotFound.vue         # 404 page
```
# 部署项目到本地
在Code下拉中选择Download ZIP，再解压至你的项目文件夹里，同时推荐使用Visual Studio Code，我个人准备了调试配置，直接在VSCode里面导入即可运行。
## 1.配置后端Django环境
首先你需要创建并启动虚拟环境（我用的是Python3.13），在项目根目录打开 PowerShell，并执行以下命令：
```
cd YOUR_PROJECT_ROOT_DIR\NEV_Price_System
```
```
python -m venv .venv
```
```
.\.venv\Scripts\Activate.ps1
```
```
python -m pip install --upgrade pip
```
确保你的终端输出如下，代表你的虚拟环境成功启动
```
(.venv) PS YOUR_PROJECT_ROOT_DIR\NEV_Price_System> 
```
现在安装本系统所需依赖，我在项目中保存了requiremen.txt方便快速安装依赖，运行以下命令（确保pip为最新，且Python版本大于等于3.13）：
```
pip install -r requirements.txt
```
等待所有依赖安装好，你可以开始配置数据库了。
## 2.配置数据库
这里推荐使用MySQL和PostgreSQL，Django默认使用SQLlite3（但是我没怎么用过，而且迁移时间长），确保你的电脑安装这些数据库应用，安装依赖：
### MySQL
```
pip install pymysql
```
### PostgreSQL
```
pip install psycopg2-binary
```
然后修改Django全局配置文件为自己的数据库名称等（Postgre示例）
```
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'YOUR_DB_NAME',
    'USER': 'YOUR_DB_USER',
    'PASSWORD': 'YOUR_DB_PASSWORD',
    'HOST': '127.0.0.1',
    'PORT': '5432',
  }
}
```
迁移数据库（这部分自动迁移数据库表，无需自己用SQL创建，我这里采用Django数据库迁移命令，你只需创建一个数据库即可）
```
python manage.py makemigrations
```
```
python manage.py migrate
```
写入车型数据（可选）我在static\data里面有一份car_data_15features.xlsx是训练XGBoost模型的示例数据，可以直接通过运行import_data.py和updat_data.py这两个脚本来写入数据到你的数据库，当然你也可以使用自己的数据，不过这边我的系统可能只参考我的数据格式，你可以把你的数据修改成我的格式，如car_data_15features.xlsx一样，应该也可以写入，后续我会提到。
### 第一次写入（全局Create）
```
python manage.py import_data
```
### 后续写入（更新数据）
```
python manage.py update_data
```
写入成功后可以创建Django管理员账号来直接检查是否成功部署（你也可以直接使用我的前端管理员入口，这个就是接的后端admin接口）
```
python manage.py createsuperuser
```
检查写入数据成功后，还需要训练模型，我这里已经写好了训练脚本脚本train_model.py，它会自动执行数据清洗和模型训练
```
python manage.py train_model
```
以上工作完成代表我的项目已经成功在你的本地部署了，接下来可以运行系统并测试了。
## 3.运行系统
首先启动后端
```
cd YOUR_PROJECT_ROOT_DIR\NEV_Price_System
```
```
python manage.py runserver 0.0.0.0:8000
```
启动前端（确保安装最新的npm和node.js）
```
cd YOUR_PROJECT_ROOT_DIR\NEV_Price_System\frontend
```
```
npm run dev
```
在你的Chrome浏览器中访问 http://localhost:5173 或者 http://127.0.0.1:5173 （确保你的电脑5173、5432、8000这三个端口没有被占用），看到用户登录页面，代表你成功将系统部署并运行了。
# Deploy the project locally
Select "Download ZIP" from the "Code" dropdown menu, then extract the file to your project folder. It is recommended to use Visual Studio Code. I have prepared a debugging configuration, which can be directly imported into VSCode for running.
## 1. Configure the backend Django environment
First, you need to create and activate a virtual environment (I am using Python 3.13). Open PowerShell in the project's root directory and execute the following commands:
```
cd YOUR_PROJECT_ROOT_DIR\NEV_Price_System
```
```
python -m venv .venv
```
```
.\.venv\Scripts\Activate.ps1
```
```
python -m pip install --upgrade pip
```
Ensure that your terminal output is as follows, indicating that your virtual environment has been successfully activated
```
(.venv) PS YOUR_PROJECT_ROOT_DIR\NEV_Price_System> 
```
Now, to install the dependencies required for this system, I have saved a `requirements.txt` file in the project for quick and easy installation. Run the following command (ensure that pip is the latest version and the Python version is greater than or equal to 3.13):
```
pip install -r requirements.txt
```
Once all dependencies are installed, you can start configuring the database.
## 2. Configure the database
Here, I recommend using MySQL and PostgreSQL. Django uses SQLite3 by default (but I haven't used it much, and the migration time is long). Make sure your computer has these database applications installed, and install the dependencies:
### MySQL
```
pip install pymysql
```
### PostgreSQL
```
pip install psycopg2-binary
```
Then modify the Django global configuration file with your own database name, etc. (PostgreSQL example)
```
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'YOUR_DB_NAME',
    'USER': 'YOUR_DB_USER',
    'PASSWORD': 'YOUR_DB_PASSWORD',
    'HOST': '127.0.0.1',
    'PORT': '5432',
  }
}
```
Migrate the database (This part automatically migrates the database tables, so there's no need to create them using SQL. I use the Django database migration command here, and you just need to create a database)
```
python manage.py makemigrations
```
```
python manage.py migrate
```
Writing vehicle model data (optional) I have a sample data file named car_data_15features.xlsx in the static\data folder, which is used to train the XGBoost model. You can directly write the data into your database by running the two scripts import_data.py and update_data.py. Of course, you can also use your own data, but my system may only recognize my data format. You can modify your data to match my format, like car_data_15features.xlsx, and it should be able to be written in. I will mention this later.
### First write (global Create)
```
python manage.py import_data
```
### Subsequent writing (updating data)
```
python manage.py update_data
```
After successful writing, you can create a Django administrator account to directly check whether the deployment is successful (you can also directly use my frontend administrator portal, which is connected to the backend admin interface)
```
python manage.py createsuperuser
```
After verifying that the data has been successfully written, it is necessary to train the model. I have already written the training script, train_model.py, which will automatically perform data cleaning and model training
```
python manage.py train_model
```
The completion of the above tasks signifies that my project has been successfully deployed on your local system. You can now run the system and proceed with testing.
## 3. Running the System
First, start the backend
```
cd YOUR_PROJECT_ROOT_DIR\NEV_Price_System
```
```
python manage.py runserver 0.0.0.0:8000
```
Start the frontend (ensure the latest npm and node.js are installed)
```
cd YOUR_PROJECT_ROOT_DIR\NEV_Price_System\frontend
```
```
npm run dev
```
Access http://localhost:5173 or http://127.0.0.1:5173 in your Chrome browser (ensure that ports 5173, 5432, and 8000 on your computer are not occupied). If you see the user login page, it means that you have successfully deployed and run the system.
