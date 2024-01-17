@echo off

REM 1. 添加所有修改
git add .

REM 2. 提交更改并使用系统时间作为提交消息
set datetime=%date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%
git commit -m "%datetime%"

REM 3. 推送到远程仓库
git push