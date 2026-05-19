#!/bin/bash

# Директории
PROTO_DIR="../proto"
OUTPUT_DIR="../generated"

# Создаём директорию для сгенерированного кода
mkdir -p $OUTPUT_DIR

# Генерация Python кода из proto файлов
python -m grpc_tools.protoc \
    -I=$PROTO_DIR \
    --python_out=$OUTPUT_DIR \
    --grpc_python_out=$OUTPUT_DIR \
    $PROTO_DIR/*.proto

echo "✅ Code generated successfully"

# Создаём __init__.py
touch $OUTPUT_DIR/__init__.py