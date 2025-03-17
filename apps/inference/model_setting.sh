#! /bin/bash

vllm serve /weights/gemma-3-27b-it \
           --task generate \
					 --dtype bfloat16 \
					 --served-model-name vllm \
					 --host 0.0.0.0 \
					 --port 8080 \
					 --api-key test123 \
					 --tensor-parallel-size 4 \
					 --pipeline-parallel-size 1 \
					 --gpu-memory-utilization 0.95 \
					 --enable-chunked-prefill \
					 --max-num-seqs 8 \
           --max-num-batched-tokens 512 \
           --max_model_len 8192