#!/usr/bin/env bash

## directories to create
directories=("app" "app/static" "app/templates" "notebooks" "notebooks/develop" "notebooks/deliver" "notebooks/archive"
"config" "config/logging" "models" "models/archive" "data" "data/sample" "data/external" "data/archive" "data/auxiliary"
"deliverables" "figures" "docs" "references" "src" "src/sql" "src/archive" "src/helpers"
"test" "test/model"  "test/model/test" "test/model/true" "test/unit")

## what to add to .gitignore
gitignore=( "__pycache__/" "*.py[cod]" "*$py.class" ".DS_Store" ".idea/" ".log" ".png" ".idea"
"*.ipynb" ".ipynb_checkpoints/" "data/*" "!data/sample/" "!data/auxiliary" "models/*" "test/model/test/*" "!.gitkeep" ".idea"
)

# what python scripts to set up with a logger
src_pyfiles=("ingest_data" "preprocess" "generate_features" "train_model" "score_model"
"evaluate_model" "postprocess" "helpers/helpers")

declare -a python_header_lines=("import logging" " " "logger = logging.getLogger(__name__)")

mkdir $1

touch $1/README.md
touch requirements.txt

for d in ${directories[@]}; do
 mkdir $1/$d
 touch $1/$d/.gitkeep
done

for g in ${gitignore[@]}; do
    echo $g >> $1/.gitignore
done

IFS=$'\n'
for f in ${src_pyfiles[@]}; do
    for p in ${python_header_lines[@]}; do
        echo $p >> $1/src/$f.py
    done
done
