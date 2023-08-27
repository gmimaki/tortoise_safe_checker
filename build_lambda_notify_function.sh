#!/bin/bash

# ディレクトリ名を指定
DIR_NAME="notify_function"

# 既存のディレクトリやzipファイルがあれば削除
rm -rf $DIR_NAME

# ディレクトリを作成
mkdir $DIR_NAME

# requirements.txtから必要なPythonモジュールをインストール
pip install -r src/notify_environment/requirements.txt -t $DIR_NAME

# Lambda関数のスクリプトをディレクトリにコピー
cp src/notify_environment/notify_environment.py $DIR_NAME/